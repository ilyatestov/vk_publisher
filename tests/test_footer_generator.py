"""
Тесты для генератора футеров
"""
import pytest
import os
import sys
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from publisher.footer_generator import FooterGenerator


@pytest.fixture
def temp_config():
    """Создание временного файла конфигурации"""
    config = {
        "telegram": {
            "channel": "@test_channel",
            "enabled": True
        },
        "vk": {
            "channel": "test_group",
            "enabled": True
        },
        "hashtags": ["#test", "#news"]
    }
    
    fd, path = tempfile.mkstemp(suffix='.json')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    
    yield path
    os.unlink(path)


@pytest.fixture
def footer_generator(temp_config):
    return FooterGenerator(social_links_config_path=temp_config)


class TestFooterGenerator:
    """Тесты для класса FooterGenerator"""
    
    def test_init(self, temp_config):
        """Тест инициализации"""
        generator = FooterGenerator(social_links_config_path=temp_config)
        
        assert generator.social_links is not None
        assert 'telegram' in generator.social_links
    
    def test_create_full_post_basic(self, footer_generator):
        """Тест создания поста без источников"""
        content = "Test content"
        
        result = footer_generator.create_full_post(content=content, sources=[])
        
        assert content in result
        assert '#test' in result or '#news' in result
    
    def test_create_full_post_with_sources(self, footer_generator):
        """Тест создания поста с источниками"""
        content = "Test content"
        sources = [
            {'title': 'Source 1', 'url': 'https://example.com/1'},
            {'title': 'Source 2', 'url': 'https://example.com/2'}
        ]
        
        result = footer_generator.create_full_post(content=content, sources=sources)
        
        assert content in result
        assert 'Source 1' in result
        assert 'https://example.com/1' in result
        assert 'Source 2' in result
    
    def test_create_full_post_with_telegram(self, footer_generator):
        """Тест создания поста с Telegram каналом"""
        content = "Test content"
        
        result = footer_generator.create_full_post(content=content, sources=[])
        
        assert 'https://t.me/test_channel' in result
    
    def test_generate_footer(self, footer_generator):
        """Тест генерации футера"""
        footer = footer_generator.generate_footer(sources=[])
        
        assert isinstance(footer, str)
        assert len(footer) > 0
        assert '━━━━━━━━' in footer
    
    def test_generate_sources_section_empty(self, footer_generator):
        """Тест генерации секции источников - пусто"""
        sources = []
        
        footer = footer_generator.generate_footer(sources=sources)
        
        assert 'Источники' not in footer or '📌 Источники' in footer
    
    def test_generate_sources_section_single(self, footer_generator):
        """Тест генерации секции источников - один источник"""
        sources = [{'title': 'Test Source', 'url': 'https://example.com'}]
        
        footer = footer_generator.generate_footer(sources=sources)
        
        assert 'Источник' in footer or 'Test Source' in footer
    
    def test_generate_sources_section_multiple(self, footer_generator):
        """Тест генерации секции источников - несколько источников"""
        sources = [
            {'title': 'Source 1', 'url': 'https://example.com/1'},
            {'title': 'Source 2', 'url': 'https://example.com/2'}
        ]
        
        footer = footer_generator.generate_footer(sources=sources)
        
        assert 'Источники' in footer
        assert 'Source 1' in footer
        assert 'Source 2' in footer
    

    def test_generate_footer_with_vk_network(self, footer_generator):
        """Тест, что VK сеть из конфигурации попадает в футер"""
        footer = footer_generator.generate_footer(sources=[])

        assert 'VK' in footer
        assert 'https://vk.com/test_group' in footer

    def test_channel_normalization_for_telegram(self, footer_generator):
        """Тест нормализации @username в URL"""
        footer = footer_generator.generate_footer(sources=[])

        assert 'https://t.me/test_channel' in footer



    def test_load_config_invalid_path(self):
        """Тест загрузки конфигурации - неверный путь"""
        generator = FooterGenerator(social_links_config_path='/nonexistent/path.json')
        
        assert generator.social_links == {}


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
