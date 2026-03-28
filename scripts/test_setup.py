#!/usr/bin/env python3
"""
Проверка готовности системы к запуску
Запуск: python scripts/test_setup.py
"""

import os
import sys
from pathlib import Path


def check_env():
    """Проверка .env файла"""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env файл не найден")
        print("   Решение: скопируйте .env.example в .env и заполните переменные")
        return False
    
    required_vars = ['VK_ACCESS_TOKEN', 'VK_GROUP_ID', 'TELEGRAM_BOT_TOKEN']
    with open(env_file) as f:
        content = f.read()
    
    missing = []
    for var in required_vars:
        # Ищем переменную и проверяем что она не пустая
        for line in content.split('\n'):
            if line.startswith(f'{var}='):
                value = line.split('=', 1)[1].strip()
                # Игнорируем комментарии после значения
                if '#' in value:
                    value = value.split('#')[0].strip()
                if not value:
                    missing.append(var)
                break
        else:
            missing.append(var)
    
    if missing:
        print(f"❌ Не заполнены переменные: {missing}")
        print("   Откройте .env и заполните требуемые значения")
        return False
    
    print("✅ .env файл настроен")
    return True


def check_dependencies():
    """Проверка установленных пакетов"""
    missing_deps = []
    
    try:
        import vk_api
    except ImportError:
        missing_deps.append('vk-api')
    
    try:
        from loguru import logger
    except ImportError:
        missing_deps.append('loguru')
    
    try:
        import aiosqlite
    except ImportError:
        missing_deps.append('aiosqlite')
    
    try:
        import aiohttp
    except ImportError:
        missing_deps.append('aiohttp')
    
    try:
        from dotenv import load_dotenv
    except ImportError:
        missing_deps.append('python-dotenv')
    
    if missing_deps:
        print(f"❌ Не установлены пакеты: {', '.join(missing_deps)}")
        print("   Решение: pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены")
    return True


def check_directories():
    """Проверка структуры папок"""
    required_dirs = ['data', 'logs', 'config']
    for dir_name in required_dirs:
        Path(dir_name).mkdir(exist_ok=True)
    
    print("✅ Папки созданы/проверены")
    return True


def check_ollama():
    """Проверка подключения к Ollama"""
    import requests
    
    ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
    try:
        resp = requests.get(f'{ollama_url}/api/tags', timeout=5)
        if resp.status_code == 200:
            print("✅ Ollama подключён")
            return True
        else:
            print(f"⚠️ Ollama вернул статус {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️ Ollama не доступен (ИИ-рерайт не будет работать)")
        print("   Если нужен ИИ: убедитесь что Ollama запущен на порту 11434")
    except Exception as e:
        print(f"⚠️ Ошибка проверки Ollama: {e}")
    
    # Это не критично, система может работать без ИИ
    return True


def main():
    print("=" * 50)
    print("ПРОВЕРКА ГОТОВНОСТИ СИСТЕМЫ")
    print("=" * 50)
    print()
    
    checks = [
        ("Конфигурация", check_env),
        ("Зависимости", check_dependencies),
        ("Структура папок", check_directories),
        ("Ollama (опционально)", check_ollama),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n[{name}]")
        result = check_func()
        results.append(result)
    
    print("\n" + "=" * 50)
    
    if all(results):
        print("✅ Система готова к запуску!")
        print("\nЗапуск:")
        print("  python src/main.py")
        print("\nИли через Docker:")
        print("  docker-compose up -d")
        sys.exit(0)
    else:
        print("❌ Есть проблемы, исправьте перед запуском")
        sys.exit(1)


if __name__ == '__main__':
    main()
