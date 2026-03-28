"""
Основной файл запуска системы автопостинга ВКонтакте
"""
import asyncio
import json
from datetime import datetime
from loguru import logger
import sys

# Добавляем src в путь импорта
sys.path.insert(0, '/app/src')

from src.database import Database
from src.vk_api_client import VKAPIClient
from src.content_fetcher import ContentFetcher
from src.processor import AIRewriter, Deduplicator
from src.publisher import VKPublisher, FooterGenerator
from src import settings


async def main():
    """Основная функция запуска системы"""
    
    # Настройка логирования
    logger.add(
        settings.log_file,
        rotation="10 MB",
        retention="7 days",
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
    )
    
    logger.info("=" * 60)
    logger.info("Запуск системы автопостинга ВКонтакте")
    logger.info("=" * 60)
    
    # Инициализация компонентов
    logger.info("Инициализация компонентов...")
    
    # База данных
    db = Database(settings.database_path)
    await db.initialize()
    
    # VK API клиент
    vk_client = VKAPIClient(
        access_token=settings.vk_access_token,
        group_id=settings.vk_group_id,
        api_version=settings.vk_api_version
    )
    
    # Сборщик контента
    content_fetcher = ContentFetcher(
        vk_api_client=vk_client,
        proxy=settings.proxy_list[0] if settings.proxy_list else None
    )
    
    # ИИ-рерайтер
    ai_rewriter = AIRewriter(
        base_url=settings.ollama_base_url,
        model=settings.llm_model
    )
    
    # Дедупликатор
    deduplicator = Deduplicator(database=db)
    
    # Публикатор
    publisher = VKPublisher(vk_api_client=vk_client, database=db)
    
    # Генератор футеров
    footer_generator = FooterGenerator(
        social_links_config_path=settings.social_links_config_path
    )
    
    # Проверка доступности модели ИИ
    logger.info("Проверка доступности ИИ модели...")
    if await ai_rewriter.check_model_availability():
        logger.success("ИИ модель доступна")
    else:
        logger.warning("ИИ модель недоступна. Рерайт будет пропущен.")
    
    # Загрузка конфигурации источников
    logger.info("Загрузка конфигурации источников...")
    sources_config = content_fetcher.load_sources(settings.sources_config_path)
    
    # Основной цикл
    posts_published_today = 0
    
    while True:
        try:
            logger.info("\n" + "=" * 60)
            logger.info(f"Начало цикла сбора контента: {datetime.now()}")
            logger.info("=" * 60)
            
            # Проверка лимита постов в день
            if posts_published_today >= settings.max_posts_per_day:
                logger.info(f"Достигнут лимит постов на сегодня: {posts_published_today}")
                await asyncio.sleep(3600)  # Ждём час
                posts_published_today = 0  # Сброс через час (в реальном приложении лучше по дате)
                continue
            
            # Сбор контента из всех источников
            logger.info("Сбор контента из источников...")
            all_content = await content_fetcher.fetch_all(sources_config)
            logger.info(f"Собрано {len(all_content)} материалов")
            
            if not all_content:
                logger.info("Нет нового контента. Ожидание...")
                await asyncio.sleep(settings.post_interval_minutes * 60)
                continue
            
            # Фильтрация дубликатов
            logger.info("Фильтрация дубликатов...")
            unique_content = await deduplicator.filter_duplicates(all_content)
            logger.info(f"Осталось {len(unique_content)} уникальных материалов")
            
            if not unique_content:
                logger.info("Все материалы - дубликаты. Ожидание...")
                await asyncio.sleep(settings.post_interval_minutes * 60)
                continue
            
            # Группировка по темам
            grouped_content = deduplicator.group_similar_articles(unique_content)
            
            # Обработка каждой группы
            for topic, articles in grouped_content.items():
                if posts_published_today >= settings.max_posts_per_day:
                    break
                
                logger.info(f"\nОбработка темы: {topic}")
                
                # Если статей несколько - объединяем
                if len(articles) > 1:
                    merged = await deduplicator.merge_articles(articles)
                    
                    # ИИ-рерайт объединённого контента
                    if merged.get('needs_rewrite'):
                        logger.info("Генерация саммари через ИИ...")
                        summary = await ai_rewriter.generate_summary(merged.get('articles', []))
                        
                        if summary:
                            content_text = summary
                        else:
                            # Если ИИ не сработал, берём первую статью
                            content_text = articles[0].get('content', '')
                    else:
                        content_text = merged.get('content', '')
                    
                    sources = merged.get('sources', [])
                    image_url = merged.get('image_url')
                    title = merged.get('title', '')
                else:
                    # Одна статья - просто рерайт
                    article = articles[0]
                    
                    logger.info("Рерайт через ИИ...")
                    rewritten = await ai_rewriter.rewrite(
                        content=article.get('content', ''),
                        title=article.get('title', '')
                    )
                    
                    content_text = rewritten if rewritten else article.get('content', '')
                    sources = [{
                        'title': article.get('title', ''),
                        'url': article.get('link', '')
                    }]
                    image_url = article.get('image_url')
                    title = article.get('title', '')
                
                # Генерация полного поста с футером
                full_post = footer_generator.create_full_post(
                    content=content_text,
                    sources=sources
                )
                
                # Подготовка данных поста
                post_data = {
                    'text': full_post,
                    'title': title,
                    'source': articles[0].get('source', 'unknown'),
                    'content_hash': articles[0].get('content_hash', ''),
                    'image_url': image_url,
                    'sources': sources
                }
                
                # Публикация
                logger.info("Публикация поста...")
                vk_post_id = await publisher.publish_post(
                    post_data=post_data,
                    enable_preview=settings.enable_preview
                )
                
                if vk_post_id:
                    posts_published_today += 1
                    logger.success(f"Пост опубликован! Всего сегодня: {posts_published_today}/{settings.max_posts_per_day}")
                    
                    # Добавление хеша в базу
                    await db.add_content_hash(
                        content_hash=post_data['content_hash'],
                        title=title,
                        source=post_data['source'],
                        post_id=vk_post_id
                    )
                else:
                    logger.error("Не удалось опубликовать пост")
            
            # Статистика
            stats = await db.get_statistics()
            logger.info(f"\nСтатистика БД: {stats}")
            
            # Ожидание следующего цикла
            next_run = datetime.now().timestamp() + (settings.post_interval_minutes * 60)
            logger.info(f"\nСледующий запуск в: {datetime.fromtimestamp(next_run)}")
            await asyncio.sleep(settings.post_interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("Остановка системы по сигналу пользователя")
            break
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            await asyncio.sleep(60)  # Ждём минуту перед перезапуском


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Система остановлена")
