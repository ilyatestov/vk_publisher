<?php

declare(strict_types=1);

namespace VkPublisher\Services;

use VkPublisher\Contracts\VkClientInterface;
use VkPublisher\DTO\PostRequest;

final readonly class PostService
{
    public function __construct(
        private VkClientInterface $client,
        private int $groupId,
    ) {
    }

    /**
     * @return array<int|string, mixed>
     */
    public function publish(PostRequest $request): array
    {
        $params = [
            'owner_id' => -abs($this->groupId),
            'message' => $request->message,
            'from_group' => $request->fromGroup,
        ];

        if ($request->publishDate !== null) {
            $params['publish_date'] = $request->publishDate;
        }

        if ($request->attachments !== []) {
            $params['attachments'] = implode(',', $request->attachments);
        }

        return $this->client->request('wall.post', $params);
    }

    /**
     * @param list<array{message: string, attachments?: list<string>}> $posts
     * @return array<int|string, mixed>
     */
    public function publishBatch(array $posts): array
    {
        $commands = [];

        foreach ($posts as $post) {
            $attachments = isset($post['attachments']) ? implode(',', $post['attachments']) : '';
            $message = addslashes($post['message']);
            $commands[] = sprintf(
                'API.wall.post({"owner_id":-%d,"from_group":1,"message":"%s","attachments":"%s"})',
                abs($this->groupId),
                $message,
                addslashes($attachments)
            );
        }

        return $this->client->executeBatch($commands);
    }
}
