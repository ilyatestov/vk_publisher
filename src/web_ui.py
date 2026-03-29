"""
VK Publisher Web UI - Gradio Interface

Простой веб-интерфейс для управления VK Publisher через Gradio.
"""
import asyncio
import gradio as gr
import httpx
from datetime import datetime
import json
from typing import Dict, Any, Tuple, List


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


async def get_social_links_config():
    """Загрузка конфигурации соцсетей из API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/api/v1/config/social-links", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return json.dumps(data.get("config", {}), ensure_ascii=False, indent=2)
            return f'{{"error": "Ошибка загрузки: {response.status_code}"}}'
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


async def fetch_social_links_dict() -> Dict[str, Any]:
    """Получение конфига соцсетей в виде словаря."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{API_BASE_URL}/api/v1/config/social-links", timeout=10)
        if response.status_code != 200:
            raise RuntimeError(f"Ошибка загрузки: {response.status_code}")
        return response.json().get("config", {}) or {}


def _network_keys(config: Dict[str, Any]) -> List[str]:
    return [k for k, v in config.items() if k not in {"hashtags", "call_to_action"} and isinstance(v, dict)]


def _hashtags_to_str(config: Dict[str, Any]) -> str:
    tags = config.get("hashtags", [])
    if isinstance(tags, list):
        return ", ".join(tags)
    return ""


def _split_hashtags(raw_tags: str) -> List[str]:
    return [tag.strip() for tag in raw_tags.split(",") if tag.strip()]


def _network_fields(config: Dict[str, Any], selected: str) -> Tuple[str, str, bool]:
    node = config.get(selected, {}) if isinstance(config, dict) else {}
    channel = node.get("channel", "") if isinstance(node, dict) else ""
    label = node.get("label", "") if isinstance(node, dict) else ""
    enabled = bool(node.get("enabled", False)) if isinstance(node, dict) else False
    return channel, label, enabled


async def load_social_links_form():
    """Загрузка конфига в форму CRUD."""
    try:
        config = await fetch_social_links_dict()
        keys = _network_keys(config)
        selected = keys[0] if keys else ""
        channel, label, enabled = _network_fields(config, selected) if selected else ("", "", False)
        return (
            config,
            gr.update(choices=keys, value=selected),
            channel,
            label,
            enabled,
            config.get("call_to_action", "🔗 Мы в соцсетях:"),
            _hashtags_to_str(config),
            "✅ Конфигурация загружена",
            json.dumps(config, ensure_ascii=False, indent=2),
        )
    except Exception as e:
        return ({}, gr.update(choices=[], value=""), "", "", False, "", "", f"❌ {e}", "{}")


def on_network_change(selected_network: str, config: Dict[str, Any]):
    """Подстановка полей выбранной соцсети."""
    channel, label, enabled = _network_fields(config or {}, selected_network)
    return channel, label, enabled


def upsert_network(
    config: Dict[str, Any],
    selected_network: str,
    network_name: str,
    channel: str,
    label: str,
    enabled: bool,
    call_to_action: str,
    hashtags_raw: str,
):
    """Создать/обновить соцсеть в конфиге."""
    config = dict(config or {})
    key = (network_name or selected_network or "").strip().lower()
    if not key:
        return config, gr.update(), "❌ Укажите имя соцсети", json.dumps(config, ensure_ascii=False, indent=2)

    config[key] = {
        "channel": channel.strip(),
        "enabled": bool(enabled),
        "label": label.strip() or key.capitalize(),
    }
    config["call_to_action"] = call_to_action.strip() or "🔗 Мы в соцсетях:"
    config["hashtags"] = _split_hashtags(hashtags_raw)

    keys = _network_keys(config)
    return (
        config,
        gr.update(choices=keys, value=key),
        f"✅ Сеть '{key}' сохранена в локальной форме",
        json.dumps(config, ensure_ascii=False, indent=2),
    )


def delete_network(config: Dict[str, Any], selected_network: str):
    """Удаление соцсети из локальной формы."""
    config = dict(config or {})
    if not selected_network:
        return config, gr.update(), "❌ Выберите сеть для удаления", json.dumps(config, ensure_ascii=False, indent=2)

    if selected_network in config:
        config.pop(selected_network, None)

    keys = _network_keys(config)
    next_key = keys[0] if keys else ""
    return (
        config,
        gr.update(choices=keys, value=next_key),
        f"✅ Сеть '{selected_network}' удалена из локальной формы",
        json.dumps(config, ensure_ascii=False, indent=2),
    )


async def save_social_links_config(config_json: str):
    """Сохранение конфигурации соцсетей через API"""
    if not config_json.strip():
        return "❌ Конфигурация пустая"

    try:
        payload = json.loads(config_json)
    except json.JSONDecodeError as e:
        return f"❌ Невалидный JSON: {e}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_BASE_URL}/api/v1/config/social-links",
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                return "✅ Конфигурация соцсетей сохранена"
            return f"❌ Ошибка сохранения: {response.status_code} — {response.text}"
    except Exception as e:
        return f"❌ Ошибка: {str(e)}"


async def save_social_links_state(config: Dict[str, Any]):
    """Сохранить текущий state-конфиг на сервер."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{API_BASE_URL}/api/v1/config/social-links",
                json=config or {},
                timeout=10
            )
            if response.status_code == 200:
                return "✅ Конфигурация сохранена на сервер"
            return f"❌ Ошибка API: {response.status_code} — {response.text}"
    except Exception as e:
        return f"❌ Ошибка: {e}"


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

        # Вкладка настроек соцсетей
        with gr.Tab("⚙️ Соцсети"):
            gr.Markdown("""
            ### Настройка блока соцсетей для футера постов
            Здесь можно загрузить и сохранить JSON-конфиг без ручного редактирования файлов на VPS.
            """)
            social_config = gr.Textbox(
                label="JSON конфигурация соцсетей",
                lines=18,
                placeholder='{"telegram":{"channel":"my_channel","enabled":true}}'
            )
            social_state = gr.State({})

            gr.Markdown("#### Визуальная CRUD-форма")
            with gr.Row():
                load_form_btn = gr.Button("📥 Загрузить конфиг в форму")
                save_form_btn = gr.Button("💾 Сохранить форму на сервер")
            with gr.Row():
                selected_network = gr.Dropdown(label="Выберите соцсеть", choices=[], value=None)
                new_network_name = gr.Textbox(label="Имя новой сети (если добавляете)", placeholder="например: instagram")
            with gr.Row():
                network_channel = gr.Textbox(label="Channel / username", placeholder="@my_channel или my_group")
                network_label = gr.Textbox(label="Label", placeholder="Например: Instagram")
                network_enabled = gr.Checkbox(label="Включена", value=True)
            with gr.Row():
                upsert_btn = gr.Button("➕ Добавить / Обновить")
                delete_btn = gr.Button("🗑️ Удалить выбранную сеть")
            call_to_action = gr.Textbox(label="Текст блока соцсетей", value="🔗 Мы в соцсетях:")
            hashtags_raw = gr.Textbox(label="Хештеги (через запятую)", placeholder="#news, #tech")
            form_status = gr.Textbox(label="Статус формы", lines=2)

            load_form_btn.click(
                fn=load_social_links_form,
                outputs=[
                    social_state,
                    selected_network,
                    network_channel,
                    network_label,
                    network_enabled,
                    call_to_action,
                    hashtags_raw,
                    form_status,
                    social_config,
                ],
            )

            selected_network.change(
                fn=on_network_change,
                inputs=[selected_network, social_state],
                outputs=[network_channel, network_label, network_enabled],
            )

            upsert_btn.click(
                fn=upsert_network,
                inputs=[
                    social_state,
                    selected_network,
                    new_network_name,
                    network_channel,
                    network_label,
                    network_enabled,
                    call_to_action,
                    hashtags_raw,
                ],
                outputs=[social_state, selected_network, form_status, social_config],
            )

            delete_btn.click(
                fn=delete_network,
                inputs=[social_state, selected_network],
                outputs=[social_state, selected_network, form_status, social_config],
            )

            save_form_btn.click(
                fn=save_social_links_state,
                inputs=[social_state],
                outputs=form_status,
            )

            gr.Markdown("#### JSON-режим (для продвинутой ручной правки)")
            with gr.Row():
                load_social_btn = gr.Button("📥 Загрузить из API")
                save_social_btn = gr.Button("💾 Сохранить в API")
            social_result = gr.Textbox(label="Результат", lines=2)

            load_social_btn.click(
                fn=get_social_links_config,
                outputs=social_config
            )

            save_social_btn.click(
                fn=save_social_links_config,
                inputs=social_config,
                outputs=social_result
            )
    
    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
