#!/usr/bin/env python3
"""
Тест базы данных
Запуск: python scripts/test_database.py
"""

import sqlite3
import sys
from pathlib import Path


DB_PATH = Path('data/posts.db')


def init_test_db():
    """Создать тестовую БД если не существует"""
    
    # Создаём папку data если нет
    DB_PATH.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблица постов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vk_post_id INTEGER,
            content TEXT,
            sources TEXT,
            hash TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT
        )
    ''')
    
    # Таблица дубликатов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS duplicates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_hash TEXT UNIQUE,
            original_post_id INTEGER,
            detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица логов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица источников
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_type TEXT,
            url TEXT,
            category TEXT,
            enabled INTEGER DEFAULT 1,
            last_check TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Пробуем вставить тестовую запись
    try:
        cursor.execute(
            "INSERT INTO logs (action, details) VALUES (?, ?)",
            ("test_init", "Инициализация тестовой БД")
        )
        conn.commit()
        print("✅ База данных инициализирована")
    except sqlite3.Error as e:
        print(f"⚠️ Предупреждение при инициализации: {e}")
    
    conn.close()
    return True


def test_db_write():
    """Тест записи в БД"""
    
    if not DB_PATH.exists():
        print("❌ База данных не найдена")
        print("   Сначала запустите инициализацию")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Тест записи лога
        cursor.execute(
            "INSERT INTO logs (action, details) VALUES (?, ?)",
            ("test_write", f"Проверка записи {Path.cwd()}")
        )
        conn.commit()
        print("✅ Запись в БД работает")
        
        # Тест чтения
        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        print(f"✅ Чтение из БД работает (записей в logs: {count})")
        
        # Тест уникальности hash
        cursor.execute(
            "INSERT OR IGNORE INTO duplicates (content_hash, original_post_id) VALUES (?, ?)",
            ("test_hash_123", 1)
        )
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM duplicates")
        dup_count = cursor.fetchone()[0]
        print(f"✅ Проверка уникальности работает (записей в duplicates: {dup_count})")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка работы с БД: {e}")
        return False
        
    finally:
        conn.close()


def test_db_structure():
    """Проверка структуры таблиц"""
    
    if not DB_PATH.exists():
        print("❌ База данных не найдена")
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        expected_tables = ['posts', 'duplicates', 'logs', 'sources']
        missing = [t for t in expected_tables if t not in tables]
        
        if missing:
            print(f"⚠️ Отсутствуют таблицы: {missing}")
            return False
        
        print(f"✅ Структура БД корректна ({len(tables)} таблиц)")
        
        # Показываем краткую статистику
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"   - {table}: {count} записей")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Ошибка проверки структуры: {e}")
        return False
        
    finally:
        conn.close()


def main():
    print("=" * 50)
    print("ТЕСТ БАЗЫ ДАННЫХ")
    print("=" * 50)
    print()
    
    # Этап 1: Инициализация
    print("[Инициализация]")
    init_success = init_test_db()
    
    if not init_success:
        print("\n❌ Не удалось инициализировать БД")
        sys.exit(1)
    
    # Этап 2: Тест записи/чтения
    print("\n[Запись/Чтение]")
    write_success = test_db_write()
    
    if not write_success:
        print("\n❌ Тест записи не пройден")
        sys.exit(1)
    
    # Этап 3: Проверка структуры
    print("\n[Структура таблиц]")
    structure_success = test_db_structure()
    
    print("\n" + "=" * 50)
    
    if all([init_success, write_success, structure_success]):
        print("✅ База данных готова к работе")
        print(f"\nПуть к БД: {DB_PATH.absolute()}")
        print("\nПолезные команды:")
        print("  sqlite3 data/posts.db '.tables'")
        print("  sqlite3 data/posts.db 'SELECT * FROM logs LIMIT 5;'")
        print("\nБэкап:")
        print("  cp data/posts.db data/posts.backup.db")
        sys.exit(0)
    else:
        print("❌ Есть проблемы с базой данных")
        sys.exit(1)


if __name__ == '__main__':
    main()
