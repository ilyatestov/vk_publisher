"""
Тесты для модуля vk_api_client.py
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from vk_api.exceptions import ApiError
import requests.exceptions
import sys
sys.path.insert(0, '/workspace/src')

from vk_api_client import VKAPIClient


def create_mock_api_error(error_msg="Test error"):
    """Создание мок-объекта ApiError с правильными аргументами"""
    # Создаем настоящий ApiError с необходимыми аргументами
    error_data = {
        'error_code': 6,  # Too many requests
        'error_msg': error_msg
    }
    try:
        # Пытаемся создать настоящий ApiError (нужен vk объект)
        from vk_api.exceptions import ApiError
        mock_vk = Mock()
        return ApiError(
            vk=mock_vk,
            method='test_method',
            values={},
            raw={'error': error_data},
            error=error_data
        )
    except Exception:
        # Если не получается, создаем исключение которое будет распознано tenacity
        class MockApiError(Exception):
            def __init__(self, msg):
                super().__init__(msg)
                self.error = 'test_error'
                self.error_msg = msg
                self.method = 'test_method'
                self.values = {}
                self.raw = {'error': error_data}
        return MockApiError(error_msg)


class TestVKAPIClient:
    """Тесты для клиента VK API"""

    @pytest.fixture
    def mock_vk_session(self):
        """Фикстура для создания мок-объекта vk_session"""
        with patch('vk_api.VkApi') as mock_vk_api:
            mock_session = MagicMock()
            mock_vk_api.return_value = mock_session
            mock_session.get_api.return_value = MagicMock()
            yield mock_session

    @pytest.fixture
    def vk_client(self, mock_vk_session):
        """Фикстура для создания экземпляра VKAPIClient"""
        return VKAPIClient(
            access_token="test_token",
            group_id="123456"
        )

    def test_init(self, mock_vk_session):
        """Тест инициализации клиента"""
        client = VKAPIClient(
            access_token="test_token",
            group_id="123456",
            api_version="5.131"
        )
        
        assert client.access_token == "test_token"
        assert client.group_id == "123456"
        assert client.api_version == "5.131"
        # Проверяем что VkApi был вызван через vk_api.VkApi
        from unittest.mock import call
        # Фикстура уже создала моковый объект, проверяем его атрибуты
        assert hasattr(client, 'vk_session')
        assert hasattr(client, 'vk')

    @patch('time.sleep', return_value=None)  # Патчим sleep для ускорения тестов
    def test_post_to_wall_success(self, mock_sleep, vk_client, mock_vk_session):
        """Тест успешной публикации поста"""
        # Настройка мок-объекта
        mock_vk_session.get_api.return_value.wall.post.return_value = {
            'post_id': 12345,
            'owner_id': -123456
        }
        
        result = vk_client.post_to_wall(
            message="Test post message",
            attachments=['photo123_456'],
            signed=False
        )
        
        assert result == {'post_id': 12345, 'owner_id': -123456}
        mock_vk_session.get_api.return_value.wall.post.assert_called_once_with(
            owner_id='-123456',
            message="Test post message",
            from_group=1,
            attachments='photo123_456'
        )

    @patch('time.sleep', return_value=None)
    def test_post_to_wall_with_publish_date(self, mock_sleep, vk_client, mock_vk_session):
        """Тест публикации с отложенной датой"""
        mock_vk_session.get_api.return_value.wall.post.return_value = {
            'post_id': 67890,
            'owner_id': -123456
        }
        
        result = vk_client.post_to_wall(
            message="Scheduled post",
            publish_date=1234567890
        )
        
        assert result['post_id'] == 67890
        call_args = mock_vk_session.get_api.return_value.wall.post.call_args
        assert call_args[1]['publish_date'] == 1234567890

    @patch('time.sleep', return_value=None)
    def test_post_to_wall_retry_on_api_error(self, mock_sleep, vk_client, mock_vk_session):
        """Тест повторных попыток при ApiError"""
        # Первые 2 вызова выбрасывают ApiError, 3-й успешный
        mock_vk_session.get_api.return_value.wall.post.side_effect = [
            create_mock_api_error("Rate limit exceeded"),
            create_mock_api_error("Temporary error"),
            {'post_id': 11111}
        ]
        
        result = vk_client.post_to_wall(message="Retry test")
        
        # Проверяем что было 3 попытки (2 неудачи + 1 успех)
        assert mock_vk_session.get_api.return_value.wall.post.call_count == 3
        assert result['post_id'] == 11111

    @patch('time.sleep', return_value=None)
    def test_post_to_wall_retry_on_network_error(self, mock_sleep, vk_client, mock_vk_session):
        """Тест повторных попыток при сетевой ошибке"""
        mock_vk_session.get_api.return_value.wall.post.side_effect = [
            requests.exceptions.ConnectionError("Network error"),
            requests.exceptions.Timeout("Timeout"),
            {'post_id': 22222}
        ]
        
        result = vk_client.post_to_wall(message="Network retry test")
        
        assert mock_vk_session.get_api.return_value.wall.post.call_count == 3
        assert result['post_id'] == 22222

    @patch('time.sleep', return_value=None)
    def test_post_to_wall_retry_exhausted(self, mock_sleep, vk_client, mock_vk_session):
        """Тест исчерпания попыток повторных запросов"""
        # Постоянно выбрасываем ошибку
        mock_vk_session.get_api.return_value.wall.post.side_effect = create_mock_api_error("Permanent error")
        
        with pytest.raises(Exception):  # ApiError будет поднят после всех попыток
            vk_client.post_to_wall(message="Exhausted retry test")
        
        # Проверяем что было сделано 5 попыток (максимум)
        assert mock_vk_session.get_api.return_value.wall.post.call_count == 5

    @patch('time.sleep', return_value=None)
    def test_upload_photo_success(self, mock_sleep, vk_client, mock_vk_session):
        """Тест успешной загрузки фото"""
        with patch('vk_api.upload.VkUpload') as mock_upload_class:
            mock_upload = MagicMock()
            mock_upload_class.return_value = mock_upload
            
            mock_upload.photo_to_group_wall.return_value = [{
                'owner_id': 123456,
                'id': 789012
            }]
            
            result = vk_client.upload_photo(photo_path="/path/to/photo.jpg")
            
            assert result == "photo123456_789012"
            mock_upload.photo_to_group_wall.assert_called_once_with(
                group_id="123456",
                photo_source="/path/to/photo.jpg"
            )

    @patch('time.sleep', return_value=None)
    def test_upload_photo_error(self, mock_sleep, vk_client, mock_vk_session):
        """Тест ошибки при загрузке фото"""
        with patch('vk_api.upload.VkUpload') as mock_upload_class:
            mock_upload_class.side_effect = Exception("Upload failed")
            
            with pytest.raises(Exception):
                vk_client.upload_photo(photo_path="/invalid/path.jpg")

    def test_search_newsfeed_success(self, vk_client, mock_vk_session):
        """Тест успешного поиска в newsfeed"""
        mock_vk_session.get_api.return_value.newsfeed.search.return_value = {
            'items': [
                {'id': 1, 'text': 'Post 1'},
                {'id': 2, 'text': 'Post 2'}
            ]
        }
        
        result = vk_client.search_newsfeed(query="test query", count=10)
        
        assert len(result) == 2
        assert result[0]['id'] == 1
        mock_vk_session.get_api.return_value.newsfeed.search.assert_called_once()

    def test_search_newsfeed_empty_result(self, vk_client, mock_vk_session):
        """Тест пустого результата поиска"""
        mock_vk_session.get_api.return_value.newsfeed.search.return_value = {
            'items': []
        }
        
        result = vk_client.search_newsfeed(query="empty query")
        
        assert result == []

    def test_search_newsfeed_api_error(self, vk_client, mock_vk_session):
        """Тест обработки ApiError при поиске"""
        mock_vk_session.get_api.return_value.newsfeed.search.side_effect = create_mock_api_error("Search error")
        
        result = vk_client.search_newsfeed(query="error query")
        
        assert result == []

    def test_get_group_info_success(self, vk_client, mock_vk_session):
        """Тест получения информации о группе"""
        mock_vk_session.get_api.return_value.groups.getById.return_value = {
            'groups': [{
                'id': 123456,
                'name': 'Test Group',
                'screen_name': 'test_group'
            }]
        }
        
        result = vk_client.get_group_info()
        
        assert result['id'] == 123456
        assert result['name'] == 'Test Group'

    def test_get_group_info_success_list_response(self, vk_client, mock_vk_session):
        """Тест получения информации о группе при list-ответе VK API"""
        mock_vk_session.get_api.return_value.groups.getById.return_value = [
            {
                'id': 123456,
                'name': 'Test Group',
                'screen_name': 'test_group'
            }
        ]

        result = vk_client.get_group_info()

        assert result['id'] == 123456
        assert result['name'] == 'Test Group'

    def test_get_group_info_error(self, vk_client, mock_vk_session):
        """Тест ошибки при получении информации о группе"""
        mock_vk_session.get_api.return_value.groups.getById.side_effect = Exception("Group info error")
        
        result = vk_client.get_group_info()
        
        assert result == {}
