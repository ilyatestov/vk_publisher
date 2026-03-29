"""
Генератор футеров для постов
"""
import json
from typing import List, Dict, Any
from urllib.parse import urlparse
from loguru import logger


class FooterGenerator:
    """Класс для генерации футеров с ссылками на источники и соцсети"""

    SOCIAL_LABELS = {
        "telegram": "Telegram",
        "youtube": "YouTube",
        "dzen": "Дзен",
        "vk": "VK",
        "instagram": "Instagram",
        "x": "X",
        "tiktok": "TikTok",
    }

    def __init__(self, social_links_config_path: str):
        """
        Инициализация генератора футеров

        Args:
            social_links_config_path: Путь к конфигурации соцсетей
        """
        self.social_links = self._load_social_links(social_links_config_path)

    def _load_social_links(self, config_path: str) -> Dict[str, Any]:
        """Загрузка конфигурации соцсетей"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при загрузке конфигурации соцсетей: {e}")
            return {}

    def _normalize_channel(self, channel: str) -> str:
        """Нормализация названия канала/аккаунта"""

        templates = {
            'telegram': f"https://t.me/{channel}",
            'youtube': f"https://youtube.com/{channel}",
            'dzen': f"https://dzen.ru/{channel}",
            'vk': f"https://vk.com/{channel}",
            'instagram': f"https://instagram.com/{channel}",
            'x': f"https://x.com/{channel}",
            'tiktok': f"https://tiktok.com/@{channel}",
        }
        return templates.get('telegram', channel)

    def _build_social_url(self, network: str, channel: str) -> str:
        """Построение URL для соцсети"""
        templates = {
            'telegram': f"https://t.me/{channel}",
            'youtube': f"https://youtube.com/{channel}",
            'dzen': f"https://dzen.ru/{channel}",
            'vk': f"https://vk.com/{channel}",
            'instagram': f"https://instagram.com/{channel}",
            'x': f"https://x.com/{channel}",
            'tiktok': f"https://tiktok.com/@{channel}",
        }
        return templates.get(network, channel)

    def _build_social_lines(self) -> List[str]:
        """Формирование блока соцсетей из конфигурации"""
        lines: List[str] = []

        call_to_action = self.social_links.get('call_to_action', '🔗 Мы в соцсетях:')
        lines.append(call_to_action)

        for network, cfg in self.social_links.items():
            if network in {'hashtags', 'call_to_action'} or not isinstance(cfg, dict):
                continue

            if not cfg.get('enabled', False):
                continue

            channel = cfg.get('channel', '')
            if not channel:
                continue

            label = cfg.get('label') or self.SOCIAL_LABELS.get(network, network.capitalize())
            url = self._build_social_url(network, channel)
            lines.append(f"• {label}: {url}")

        return lines

    def generate_footer(self, sources: List[Dict[str, str]]) -> str:
        """
        Генерация футера для поста

        Args:
            sources: Список источников

        Returns:
            Сформированный футер
        """
        footer_parts = []

        # Разделитель
        footer_parts.append("━━━━━━━━━━━━━━━━━━━━")

        # Источники
        if sources:
            footer_parts.append("📌 Источники:")
            for source in sources[:5]:  # Максимум 5 источников
                title = source.get('title', 'Источник')
                url = source.get('url', '')

                if url:
                    # Сокращаем длинные заголовки
                    if len(title) > 50:
                        title = title[:47] + "..."
                    footer_parts.append(f"• {title}: {url}")

        footer_parts.append("")

        # Соцсети
        footer_parts.extend(self._build_social_lines())
        footer_parts.append("")

        # Хештеги
        hashtags = self.social_links.get('hashtags', [])
        if hashtags:
            footer_parts.append(" ".join(hashtags[:10]))  # Максимум 10 хештегов

        return "\n".join(footer_parts)

    def create_full_post(self,
                         content: str,
                         sources: List[Dict[str, str]],
                         custom_footer: str = None) -> str:
        """
        Создание полного поста с контентом и футером

        Args:
            content: Основной контент поста
            sources: Список источников
            custom_footer: Кастомный футер (опционально)

        Returns:
            Полный текст поста
        """
        if custom_footer:
            footer = custom_footer
        else:
            footer = self.generate_footer(sources)

        full_post = f"{content}\n\n{footer}"

        # Проверка длины (VK позволяет до 16384 символов)
        if len(full_post) > 16000:
            logger.warning(f"Длина поста ({len(full_post)}) превышает рекомендуемую")
            # Обрезаем контент если нужно
            max_content_length = 16000 - len(footer) - 10
            content = content[:max_content_length] + "..."
            full_post = f"{content}\n\n{footer}"

        return full_post
