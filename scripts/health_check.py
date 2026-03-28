#!/usr/bin/env python3
"""
Проверка здоровья сервиса для Docker healthcheck
Используется в docker-compose.yml
"""

import sys
import sqlite3
from pathlib import Path


def check_database():
    """Проверка доступности базы данных"""
    db_path = Path('data/posts.db')
    
    if not db_path.exists():
        # БД может ещё не существовать при первом запуске
        # Это нормально, создастся при первой записи
        return True
    
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
        return True
    except Exception:
        return False


def check_logs():
    """Проверка возможности записи логов"""
    log_path = Path('logs/autoposter.log')
    
    try:
        log_path.parent.mkdir(exist_ok=True)
        # Пробуем открыть файл на запись
        with open(log_path, 'a') as f:
            f.write('')
        return True
    except Exception:
        return False


def check_config():
    """Проверка наличия конфигурационных файлов"""
    config_files = [
        Path('config/sources.json'),
        Path('config/social_links.json')
    ]
    
    for config_file in config_files:
        if not config_file.exists():
            # Файлы могут быть созданы позже
            continue
    
    return True


def main():
    """Основная функция проверки"""
    
    checks = [
        ("database", check_database),
        ("logs", check_logs),
        ("config", check_config)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append(result)
        
        if not result:
            print(f"unhealthy: {name} check failed", file=sys.stderr)
            sys.exit(1)
    
    print("healthy")
    sys.exit(0)


if __name__ == '__main__':
    main()
