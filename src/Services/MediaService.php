<?php

declare(strict_types=1);

namespace VkPublisher\Services;

use GuzzleHttp\ClientInterface;
use GuzzleHttp\Exception\GuzzleException;
use GuzzleHttp\Psr7\MultipartStream;
use GuzzleHttp\Utils;
use VkPublisher\Contracts\VkClientInterface;
use VkPublisher\DTO\PhotoUploadRequest;
use VkPublisher\Exceptions\VkApiException;

final readonly class MediaService
{
    public function __construct(
        private VkClientInterface $vkClient,
        private ClientInterface $httpClient,
        private int $groupId,
    ) {
    }

    public function uploadWallPhoto(PhotoUploadRequest $request): string
    {
        $uploadServer = $this->vkClient->request('photos.getWallUploadServer', [
            'group_id' => $this->groupId,
        ]);

        $uploadUrl = (string) ($uploadServer['upload_url'] ?? '');
        if ($uploadUrl === '') {
            throw new VkApiException('Unable to resolve VK upload URL.');
        }

        try {
            $multipart = new MultipartStream([
                [
                    'name' => 'photo',
                    'contents' => fopen($request->filePath, 'rb'),
                    'filename' => basename($request->filePath),
                ],
            ]);

            $response = $this->httpClient->request('POST', $uploadUrl, [
                'headers' => ['Content-Type' => 'multipart/form-data; boundary=' . $multipart->getBoundary()],
                'body' => $multipart,
                'timeout' => 20,
                'connect_timeout' => 3,
            ]);
        } catch (GuzzleException $e) {
            throw new VkApiException('Failed to upload media to VK.', 0, $e->getMessage());
        }

        /** @var array<string, mixed> $uploaded */
        $uploaded = Utils::jsonDecode((string) $response->getBody(), true);

        $saved = $this->vkClient->request('photos.saveWallPhoto', [
            'group_id' => $this->groupId,
            'photo' => (string) ($uploaded['photo'] ?? ''),
            'server' => (string) ($uploaded['server'] ?? ''),
            'hash' => (string) ($uploaded['hash'] ?? ''),
            'caption' => $request->caption ?? '',
        ]);

        $first = null;
        foreach ($saved as $item) {
            if (is_array($item) && isset($item['owner_id'], $item['id'])) {
                /** @var array{owner_id:int,id:int} $item */
                $first = $item;
                break;
            }
        }

        if ($first === null) {
            throw new VkApiException('VK did not return photo metadata after upload.');
        }

        return sprintf('photo%d_%d', $first['owner_id'], $first['id']);
    }
}
