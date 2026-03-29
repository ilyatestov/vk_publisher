<?php

declare(strict_types=1);

namespace VkPublisher\Tests\Unit;

use GuzzleHttp\Client;
use GuzzleHttp\Handler\MockHandler;
use GuzzleHttp\HandlerStack;
use GuzzleHttp\Psr7\Response;
use PHPUnit\Framework\MockObject\MockObject;
use PHPUnit\Framework\TestCase;
use VkPublisher\Contracts\VkClientInterface;
use VkPublisher\DTO\PhotoUploadRequest;
use VkPublisher\Services\MediaService;

final class MediaServiceTest extends TestCase
{
    /** @var VkClientInterface&MockObject */
    private VkClientInterface $vkClient;

    protected function setUp(): void
    {
        $this->vkClient = $this->createMock(VkClientInterface::class);
    }

    public function testUploadPhotoReturnsAttachmentToken(): void
    {
        $tmpFile = tempnam(sys_get_temp_dir(), 'vk_');
        file_put_contents($tmpFile, 'binary');

        $this->vkClient
            ->method('request')
            ->willReturnOnConsecutiveCalls(
                ['upload_url' => 'https://upload.vk.test'],
                [['owner_id' => -7, 'id' => 11]],
            );

        $http = new Client([
            'handler' => HandlerStack::create(new MockHandler([
                new Response(200, [], json_encode([
                    'photo' => '{"sizes":[]}',
                    'server' => 10,
                    'hash' => 'abc',
                ], JSON_THROW_ON_ERROR)),
            ])),
        ]);

        $service = new MediaService($this->vkClient, $http, 7);

        self::assertSame('photo-7_11', $service->uploadWallPhoto(new PhotoUploadRequest($tmpFile)));

        unlink($tmpFile);
    }
}
