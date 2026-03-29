<?php

declare(strict_types=1);

namespace VkPublisher\Tests\Unit;

use PHPUnit\Framework\MockObject\MockObject;
use PHPUnit\Framework\TestCase;
use VkPublisher\Contracts\VkClientInterface;
use VkPublisher\DTO\PostRequest;
use VkPublisher\Services\PostService;

final class PostServiceTest extends TestCase
{
    /** @var VkClientInterface&MockObject */
    private VkClientInterface $client;

    protected function setUp(): void
    {
        $this->client = $this->createMock(VkClientInterface::class);
    }

    public function testPublishSendsMappedParams(): void
    {
        $service = new PostService($this->client, 777);
        $future = time() + 3600;

        $this->client
            ->expects(self::once())
            ->method('request')
            ->with('wall.post', self::callback(static function (array $params) use ($future): bool {
                return $params['owner_id'] === -777
                    && $params['publish_date'] === $future
                    && $params['attachments'] === 'photo1_2'
                    && $params['from_group'] === 1;
            }))
            ->willReturn(['post_id' => 123]);

        $response = $service->publish(new PostRequest('Hello', $future, ['photo1_2']));

        self::assertSame(123, $response['post_id']);
    }
}
