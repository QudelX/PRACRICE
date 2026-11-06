import sqlite3
import time
import random


def is_prime_v1(n):
    """Медленная проверка числа на простоту (перебор всех чисел)"""
    if n < 2:
        return False
    for i in range(2, n):
        if n % i == 0:
            return False
    return True


def run_experiment():
    conn = sqlite3.connect('experiment_v1.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            number INTEGER,
            is_prime INTEGER
        )
    ''')
    conn.commit()

    print("Запуск Версии 1 (Медленные вычисления и построчная запись в БД)...")
    start_time = time.time()

    numbers = [random.randint(1000, 50000) for _ in range(5000)]

    for num in numbers:
        result = 1 if is_prime_v1(num) else 0
        cursor.execute("INSERT INTO results (number, is_prime) VALUES (?, ?)", (num, result))
        conn.commit()

    end_time = time.time()
    total_time = end_time - start_time
    print(f"Эксперимент Версии 1 успешно завершен!")
    print(f"Время выполнения: {total_time:.4f} секунд.\n")

    conn.close()


if __name__ == "__main__":
    run_experiment()
