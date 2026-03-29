<?php

declare(strict_types=1);

namespace VkPublisher\Client;

use GuzzleHttp\Client;
use GuzzleHttp\ClientInterface;
use GuzzleHttp\Exception\GuzzleException;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Middleware;
use GuzzleHttp\Utils;
use Psr\Http\Message\RequestInterface;
use Psr\Http\Message\ResponseInterface;
use Psr\Log\LoggerInterface;
use Psr\Log\NullLogger;
use VkPublisher\Config\VkConfig;
use VkPublisher\Contracts\VkClientInterface;
use VkPublisher\Exceptions\CaptchaRequiredException;
use VkPublisher\Exceptions\RateLimitException;
use VkPublisher\Exceptions\VkApiException;

final class VkApiClient implements VkClientInterface
{
    private readonly ClientInterface $httpClient;

    public function __construct(
        private readonly VkConfig $config,
        ?ClientInterface $httpClient = null,
        private readonly LoggerInterface $logger = new NullLogger(),
    ) {
        $this->httpClient = $httpClient ?? $this->buildDefaultClient();
    }

    public function request(string $method, array $params = []): array
    {
        $payload = array_merge($params, [
            'access_token' => $this->config->accessToken,
            'v' => $this->config->apiVersion,
        ]);

        try {
            $response = $this->httpClient->request('POST', $method, [
                'form_params' => $payload,
                'http_errors' => false,
            ]);
        } catch (GuzzleException $e) {
            $this->logger->error('VK HTTP request failed.', [
                'method' => $method,
                'error' => $e->getMessage(),
            ]);

            throw new VkApiException('Failed to call VK API endpoint.', 0, $e->getMessage());
        }

        /** @var array<int|string, mixed> $data */
        $data = Utils::jsonDecode((string) $response->getBody(), true);

        if (isset($data['error']) && is_array($data['error'])) {
            $this->throwVkError($data['error']);
        }

        if (!isset($data['response']) || !is_array($data['response'])) {
            throw new VkApiException('VK API returned malformed response payload.');
        }

        return $data['response'];
    }

    public function executeBatch(array $commands): array
    {
        $code = 'return [' . implode(',', $commands) . '];';

        return $this->request('execute', ['code' => $code]);
    }

    private function buildDefaultClient(): ClientInterface
    {
        $stack = HandlerStack::create();
        $stack->push(Middleware::retry(...$this->buildRetryCallbacks()));

        return new Client([
            'base_uri' => $this->config->baseUri,
            'timeout' => $this->config->timeoutSeconds,
            'connect_timeout' => $this->config->connectTimeoutSeconds,
            'handler' => $stack,
            'headers' => [
                'Accept' => 'application/json',
                'User-Agent' => 'vk-publisher-php-client/2.0',
            ],
        ]);
    }

    /**
     * @return array{0: callable(int, RequestInterface, ?ResponseInterface, ?\Throwable): bool, 1: callable(int): int}
     */
    private function buildRetryCallbacks(): array
    {
        return [
            function (
                int $retries,
                RequestInterface $request,
                ?ResponseInterface $response = null,
                ?\Throwable $exception = null
            ): bool {
                if ($retries >= $this->config->maxRetries) {
                    return false;
                }

                if ($exception !== null) {
                    return true;
                }

                if ($response === null) {
                    return false;
                }

                if ($response->getStatusCode() >= 500) {
                    return true;
                }

                $body = (string) $response->getBody();
                $decoded = json_decode($body, true);
                $errorCode = (int) ($decoded['error']['error_code'] ?? 0);

                return in_array($errorCode, [6, 9, 29], true);
            },
            function (int $retryNumber): int {
                return (int) (200 * (2 ** $retryNumber));
            },
        ];
    }

    /**
     * @param array<int|string, mixed> $error
     */
    private function throwVkError(array $error): never
    {
        $code = (int) ($error['error_code'] ?? 0);
        $message = (string) ($error['error_msg'] ?? 'Unknown VK API error');

        if ($code === 14) {
            throw new CaptchaRequiredException(
                message: $message,
                captchaSid: (string) ($error['captcha_sid'] ?? ''),
                captchaImg: (string) ($error['captcha_img'] ?? ''),
            );
        }

        if (in_array($code, [6, 9, 29], true)) {
            throw new RateLimitException('VK API rate limit exceeded.', $code, $message);
        }

        throw new VkApiException('VK API responded with an error.', $code, $message);
    }
}
