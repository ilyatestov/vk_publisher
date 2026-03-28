#!/usr/bin/env python3
"""
Тест подключения к VK API
Запуск: python scripts/test_vk_api.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Добавляем корень проекта в путь для импортов
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()


def test_vk_connection():
    """Проверка подключения к VK API и прав доступа"""
    
    token = os.getenv('VK_ACCESS_TOKEN')
    group_id = os.getenv('VK_GROUP_ID')
    
    if not token or not group_id:
        print("❌ VK_ACCESS_TOKEN или VK_GROUP_ID не настроены")
        print("   Заполните эти переменные в файле .env")
        return False
    
    # Проверяем формат токена (должен начинаться с vk1.a.)
    if not token.startswith('vk'):
        print("⚠️ Токен имеет нестандартный формат")
        print("   Убедитесь что скопировали токен полностью из https://dev.vk.com/")
    
    try:
        import vk_api
        
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        # Проверка доступа к группе
        try:
            group = vk.groups.getById(group_id=group_id)
            group_name = group[0]['name']
            print(f"✅ Подключено к группе: {group_name}")
        except vk_api.exceptions.ApiError as e:
            if e.code == 15:
                print("❌ Ошибка доступа: группа не найдена или токен не имеет прав")
                print(f"   Код ошибки VK: {e.code}")
                print("   Проверьте что:")
                print("   1. Группа существует")
                print("   2. Токен выдан для этого сообщества")
                print("   3. У токена есть право 'groups'")
            elif e.code == 5:
                print("❌ Неверный токен доступа")
                print("   Получите новый токен в https://dev.vk.com/")
            else:
                print(f"❌ Ошибка VK API (код {e.code}): {e}")
            return False
        
        # Проверка права на публикацию на стену
        try:
            # Пробуем получить информацию о стене
            wall = vk.wall.get(owner_id=-int(group_id), count=1)
            print("✅ Права на чтение стены подтверждены")
            
            # NOTE: Полная проверка права на публикацию требует попытки поста
            # Это можно сделать только в production режиме
            print("✅ Права на публикацию предполагаются (требуется тестовый пост для проверки)")
            
        except vk_api.exceptions.ApiError as e:
            if e.code == 6:
                print("⚠️ Слишком много запросов, подождите немного")
            else:
                print(f"⚠️ Проверка прав на стену: {e}")
        
        return True
        
    except ImportError:
        print("❌ Пакет vk-api не установлен")
        print("   Решение: pip install vk-api")
        return False
        
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        print("   Попробуйте запустить с DEBUG_MODE=true для подробных логов")
        return False


def main():
    print("=" * 50)
    print("ТЕСТ ПОДКЛЮЧЕНИЯ К VK API")
    print("=" * 50)
    print()
    
    success = test_vk_connection()
    
    print()
    print("=" * 50)
    
    if success:
        print("✅ VK API готов к работе")
        print("\nСледующие шаги:")
        print("  1. Запустите python src/main.py")
        print("  2. Проверьте логи на наличие ошибок")
        sys.exit(0)
    else:
        print("❌ Есть проблемы с подключением к VK")
        print("\nПолезные ссылки:")
        print("  - Получение токена: https://dev.vk.com/")
        print("  - Документация API: https://dev.vk.com/legacy/methods")
        sys.exit(1)


if __name__ == '__main__':
    main()
