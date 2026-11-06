import sqlite3
import time
import random
import math


def is_prime_v2(n):
    """Быстрая проверка числа на простоту (перебор только до корня из n)"""
    if n < 2:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def run_experiment():
    conn = sqlite3.connect('experiment_v2.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER,
            is_prime INTEGER
        )
    ''')
    conn.commit()

    print("Запуск Версии 2 (Оптимизированные вычисления и пакетная запись)...")
    start_time = time.time()

    numbers = [random.randint(1000, 50000) for _ in range(5000)]

    data_to_insert = []
    for num in numbers:
        result = 1 if is_prime_v2(num) else 0
        data_to_insert.append((num, result))

    cursor.executemany("INSERT INTO results (number, is_prime) VALUES (?, ?)", data_to_insert)
    conn.commit()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Эксперимент Версии 2 успешно завершен!")
    print(f"Время выполнения: {total_time:.4f} секунд.\n")

    conn.close()


if __name__ == "__main__":
    run_experiment()
