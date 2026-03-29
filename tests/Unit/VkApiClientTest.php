<?php

declare(strict_types=1);

namespace VkPublisher\Tests\Unit;

use GuzzleHttp\Client;
use GuzzleHttp\Handler\MockHandler;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Psr7\Response;
use PHPUnit\Framework\TestCase;
use Psr\Log\NullLogger;
use VkPublisher\Client\VkApiClient;
use VkPublisher\Config\VkConfig;
use VkPublisher\Exceptions\RateLimitException;

final class VkApiClientTest extends TestCase
{
    public function testThrowsRateLimitExceptionOnVkErrorCode(): void
    {
        $mock = new MockHandler([
            new Response(200, [], json_encode([
                'error' => ['error_code' => 6, 'error_msg' => 'Too many requests'],
            ], JSON_THROW_ON_ERROR)),
        ]);

        $client = new Client(['handler' => HandlerStack::create($mock), 'base_uri' => 'https://api.vk.com/method/']);
        $vk = new VkApiClient(
            new VkConfig(accessToken: 'token'),
            $client,
            new NullLogger(),
        );

        $this->expectException(RateLimitException::class);
        $vk->request('wall.post');
    }
}
