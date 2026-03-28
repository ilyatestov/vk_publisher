"""
VK Publisher Web UI - Gradio Interface

Простой веб-интерфейс для управления VK Publisher через Gradio.
"""
import asyncio
import gradio as gr
import httpx
from datetime import datetime


API_BASE_URL = "http://localhost:8000"


async def check_health():
    """Проверка здоровья приложения"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                return "✅ Приложение работает нормально"
            else:
                return f"❌ Ошибка: {response.status_code}"
    except Exception as e:
        return f"❌ Не удалось подключиться: {str(e)}"


async def get_statistics():
    """Получение статистики"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/stats", timeout=5)
            if response.status_code == 200:
                data = response.json()
                stats = data.get("statistics", {})
                
                result = "📊 **Статистика публикаций:**\n\n"
                result += f"- Всего постов: {stats.get('total_posts', 0)}\n"
                result += f"- Опубликованно: {stats.get('published', 0)}\n"
                result += f"- В ожидании: {stats.get('pending', 0)}\n"
                result += f"- Ошибок: {stats.get('errors', 0)}\n"
                
                return result
            else:
                return f"❌ Ошибка получения статистики: {response.status_code}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


async def add_content_source(source_url: str, source_type: str):
    """Добавление источника контента"""
    if not source_url:
        return "❌ Введите URL источника"
    
    try:
        async with httpx.AsyncClient() as client:
            # Здесь должен быть реальный API endpoint для добавления источников
            # Пока заглушка
            return f"✅ Источник добавлен: {source_url} (тип: {source_type})\n\n⚠️ Примечание: Эта функция требует реализации API endpoint"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


async def create_post_manual(content: str, schedule_time: str):
    """Создание поста вручную"""
    if not content:
        return "❌ Введите содержимое поста"
    
    try:
        async with httpx.AsyncClient() as client:
            # Заглушка для будущего API
            result = f"✅ Пост создан:\n\n{content[:100]}..."
            if schedule_time:
                result += f"\n🕐 Запланирован на: {schedule_time}"
            else:
                result += "\n📤 Будет опубликован немедленно"
            
            return result + "\n\n⚠️ Примечание: Эта функция требует реализации API endpoint"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


async def get_recent_posts():
    """Получение последних постов"""
    try:
        async with httpx.AsyncClient() as client:
            # Заглушка для будущего API
            return """📝 **Последние посты:**

1. Пример поста #1
   Статус: ✅ Опубликован
   Дата: 2024-01-15 10:30

2. Пример поста #2
   Статус: ⏳ В ожидании
   Дата: 2024-01-15 14:00

3. Пример поста #3
   Статус: ❌ Ошибка
   Дата: 2024-01-14 18:45

⚠️ Примечание: Требуется реализация API endpoint"""
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


def create_ui():
    """Создание Gradio интерфейса"""
    
    with gr.Blocks(title="VK Publisher UI", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🚀 VK Publisher - Панель управления
        
        Веб-интерфейс для управления автопостингом ВКонтакте
        """)
        
        # Вкладка состояния
        with gr.Tab("📊 Состояние"):
            health_status = gr.Textbox(label="Статус приложения")
            refresh_btn = gr.Button("🔄 Обновить")
            refresh_btn.click(fn=check_health, outputs=health_status)
            
            stats_output = gr.Textbox(label="Статистика", lines=10)
            stats_btn = gr.Button("📈 Получить статистику")
            stats_btn.click(fn=get_statistics, outputs=stats_output)
        
        # Вкладка источников контента
        with gr.Tab("📰 Источники контента"):
            gr.Markdown("### Добавить источник контента")
            source_url = gr.Textbox(
                label="URL источника",
                placeholder="https://example.com/rss или https://vk.com/public123"
            )
            source_type = gr.Dropdown(
                choices=["RSS", "VK Group", "Website"],
                value="RSS",
                label="Тип источника"
            )
            add_source_btn = gr.Button("➕ Добавить источник")
            source_result = gr.Textbox(label="Результат", lines=3)
            
            add_source_btn.click(
                fn=add_content_source,
                inputs=[source_url, source_type],
                outputs=source_result
            )
        
        # Вкладка создания постов
        with gr.Tab("✍️ Создать пост"):
            gr.Markdown("### Создание публикации вручную")
            post_content = gr.Textbox(
                label="Содержимое поста",
                placeholder="Введите текст поста...",
                lines=5
            )
            schedule_time = gr.DateTime(
                label="Запланировать время (опционально)",
                type="datetime"
            )
            create_post_btn = gr.Button("📤 Создать пост")
            post_result = gr.Textbox(label="Результат", lines=5)
            
            create_post_btn.click(
                fn=create_post_manual,
                inputs=[post_content, schedule_time],
                outputs=post_result
            )
        
        # Вкладка просмотра постов
        with gr.Tab("📋 Последние посты"):
            view_posts_btn = gr.Button("🔄 Обновить список")
            posts_output = gr.Textbox(label="Посты", lines=15)
            
            view_posts_btn.click(fn=get_recent_posts, outputs=posts_output)
        
        # Вкладка документации
        with gr.Tab("📚 Документация"):
            gr.Markdown("""
            ## 🔗 Полезные ссылки
            
            - **Swagger UI (API документация):** http://localhost:8000/docs
            - **Health Check:** http://localhost:8000/health
            - **Metrics Prometheus:** http://localhost:8000/metrics
            
            ## 🛠️ Настройка
            
            1. Получите токены API следуя инструкции `docs/VK_API_SETUP.md`
            2. Заполните файл `.env`
            3. Запустите приложение: `uvicorn src.main:app --host 0.0.0.0 --port 8000`
            4. Откройте этот интерфейс
            
            ## 📖 Полные инструкции
            
            - Установка на Windows: `docs/WINDOWS_INSTALL.md`
            - Установка на Ubuntu/VPS: `docs/UBUNTU_VPS_INSTALL.md`
            - Получение VK API токена: `docs/VK_API_SETUP.md`
            """)
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
