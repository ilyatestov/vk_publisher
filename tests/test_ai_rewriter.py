"""
Тесты для модуля ai_rewriter.py
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock
import aiohttp
import sys
sys.path.insert(0, '/workspace/src')

from processor.ai_rewriter import AIRewriter


class AsyncContextManagerMock:
    """Мок для асинхронного контекстного менеджера"""
    def __init__(self, response):
        self.response = response
    
    async def __aenter__(self):
        return self.response
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


class TestAIRewriter:
    """Тесты для ИИ-рерайтера"""

    @pytest.fixture
    def rewriter(self):
        """Фикстура для создания экземпляра AIRewriter"""
        return AIRewriter(
            base_url="http://test-ollama:11434",
            model="qwen2.5:1.5b"
        )

    @pytest.mark.asyncio
    async def test_rewrite_success(self, rewriter):
        """Тест успешного рерайта текста"""
        mock_response_data = {
            'response': 'Это переписанный текст с эмодзи 🚀 и призывом к действию!'
        }
        
        # Создаем мок для ответа
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        # Создаем мок для session.post который возвращает контекстный менеджер
        mock_cm = AsyncContextManagerMock(mock_response)
        
        with patch('aiohttp.ClientSession') as MockSession:
            mock_session_instance = AsyncMock()
            mock_session_instance.post = MagicMock(return_value=mock_cm)
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await rewriter.rewrite(
                content="Исходный текст статьи",
                title="Заголовок статьи",
                max_length=1500,
                min_length=500,
                add_emojis=True,
                add_call_to_action=True
            )
            
            assert result is not None
            assert "переписанный" in result.lower() or "🚀" in result

    @pytest.mark.asyncio
    async def test_rewrite_empty_response(self, rewriter):
        """Тест обработки пустого ответа от ИИ"""
        mock_response_data = {'response': ''}
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        mock_cm = AsyncContextManagerMock(mock_response)
        
        with patch('aiohttp.ClientSession') as MockSession:
            mock_session_instance = AsyncMock()
            mock_session_instance.post = MagicMock(return_value=mock_cm)
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await rewriter.rewrite(content="Исходный текст")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_rewrite_api_error(self, rewriter):
        """Тест обработки ошибки API"""
        mock_response = AsyncMock()
        mock_response.status = 500
        
        mock_cm = AsyncContextManagerMock(mock_response)
        
        with patch('aiohttp.ClientSession') as MockSession:
            mock_session_instance = AsyncMock()
            mock_session_instance.post = MagicMock(return_value=mock_cm)
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await rewriter.rewrite(content="Исходный текст")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_rewrite_network_error_retry(self, rewriter):
        """Тест повторных попыток при сетевой ошибке"""
        call_count = 0
        
        # Создаем моки для ответов заранее
        error_response_cm = AsyncMock()
        error_response_cm.__aenter__ = AsyncMock(side_effect=aiohttp.ClientConnectionError("Network error"))
        error_response_cm.__aexit__ = AsyncMock(return_value=None)
        
        success_response = AsyncMock()
        success_response.status = 200
        success_response.json = AsyncMock(return_value={'response': 'Success after retry'})
        success_cm = AsyncContextManagerMock(success_response)
        
        def create_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                return error_response_cm
            else:
                return success_cm
        
        with patch('aiohttp.ClientSession') as MockSession:
            mock_session_instance = AsyncMock()
            mock_session_instance.post = MagicMock(side_effect=create_side_effect)
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)
            
            result = await rewriter.rewrite(content="Retry test")
            
            assert result is not None
            assert call_count == 3  # Проверяем что было 3 попытки

    @pytest.mark.asyncio
    async def test_rewrite_timeout_retry(self, rewriter):
        """Тест повторных попыток при таймауте"""
        # Создаем мок который всегда выбрасывает TimeoutError
        timeout_response_cm = AsyncMock()
        timeout_response_cm.__aenter__ = AsyncMock(side_effect=asyncio.TimeoutError("Request timeout"))
        timeout_response_cm.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession') as MockSession:
            mock_session_instance = AsyncMock()
            mock_session_instance.post = MagicMock(return_value=timeout_response_cm)
            MockSession.return_value.__aenter__ = AsyncMock(return_value=mock_session_instance)
            MockSession.return_value.__aexit__ = AsyncMock(return_value=None)
            
            with pytest.raises(asyncio.TimeoutError):
                await rewriter.rewrite(content="Timeout test")
            
            # Проверяем что было сделано 3 попытки (max для rewrite)
            assert mock_session_instance.post.call_count == 3

    @pytest.mark.asyncio
    async def test_generate_summary_success(self, rewriter):
        """Тест успешной генерации саммари"""
        articles = [
            {'title': 'Article 1', 'content': 'Content of article 1'},
            {'title': 'Article 2', 'content': 'Content of article 2'}
        ]
        
        mock_response_data = {'response': 'Combined summary of all articles'}
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.post = MagicMock(return_value=mock_context_manager)
        
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_context):
            result = await rewriter.generate_summary(articles)
            
            assert result is not None
            assert "summary" in result.lower() or "Combined" in result
            mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_summary_empty_articles(self, rewriter):
        """Тест генерации саммари с пустым списком статей"""
        result = await rewriter.generate_summary([])
        
        assert result is None

    @pytest.mark.asyncio
    async def test_check_model_availability_success(self, rewriter):
        """Тест успешной проверки доступности модели"""
        mock_response_data = {
            'models': [
                {'name': 'qwen2.5:1.5b'},
                {'name': 'llama3.1:8b'}
            ]
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_context_manager)
        
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_context):
            result = await rewriter.check_model_availability()
            
            assert result is True

    @pytest.mark.asyncio
    async def test_check_model_availability_not_found(self, rewriter):
        """Тест когда модель не найдена"""
        mock_response_data = {
            'models': [
                {'name': 'llama3.1:8b'},
                {'name': 'mistral:7b'}
            ]
        }
        
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_response_data)
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_context_manager)
        
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_context):
            result = await rewriter.check_model_availability()
            
            assert result is False

    @pytest.mark.asyncio
    async def test_check_model_availability_server_error(self, rewriter):
        """Тест ошибки сервера при проверке модели"""
        mock_response = AsyncMock()
        mock_response.status = 503
        
        mock_context_manager = AsyncMock()
        mock_context_manager.__aenter__ = AsyncMock(return_value=mock_response)
        mock_context_manager.__aexit__ = AsyncMock(return_value=None)
        
        mock_session = AsyncMock()
        mock_session.get = MagicMock(return_value=mock_context_manager)
        
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_context):
            result = await rewriter.check_model_availability()
            
            assert result is False

    @pytest.mark.asyncio
    async def test_check_model_availability_network_error(self, rewriter):
        """Тест сетевой ошибки при проверке модели"""
        mock_session = AsyncMock()
        mock_session.get = MagicMock(side_effect=aiohttp.ClientConnectionError("Connection failed"))
        
        mock_session_context = AsyncMock()
        mock_session_context.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_context.__aexit__ = AsyncMock(return_value=None)
        
        with patch('aiohttp.ClientSession', return_value=mock_session_context):
            result = await rewriter.check_model_availability()
            
            assert result is False

    def test_create_prompt_structure(self, rewriter):
        """Тест структуры создаваемого промпта"""
        prompt = rewriter._create_prompt(
            content="Test content",
            title="Test Title",
            max_length=1000,
            min_length=500,
            add_emojis=True,
            add_call_to_action=True
        )
        
        assert isinstance(prompt, str)
        assert "Test Title" in prompt
        assert "Test content" in prompt
        assert "1000" in prompt
        assert "500" in prompt
        assert "эмодзи" in prompt.lower()
        assert "призыв к действию" in prompt.lower()

    def test_create_prompt_without_optional_features(self, rewriter):
        """Тест промпта без дополнительных функций"""
        prompt = rewriter._create_prompt(
            content="Test content",
            title="",
            max_length=1000,
            min_length=500,
            add_emojis=False,
            add_call_to_action=False
        )
        
        assert "Без названия" in prompt
        assert "эмодзи" not in prompt.lower()
        assert "призыв к действию" not in prompt.lower()
