import sqlite3
import os

conn = sqlite3.connect('test.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS people (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT
)
''')

cursor.execute("INSERT INTO people (name, city) VALUES ('Анна', 'Москва')")
cursor.execute("INSERT INTO people (name, city) VALUES ('Петр', 'Санкт-Петербург')")

conn.commit()

cursor.execute("SELECT * FROM people")
results = cursor.fetchall()

print("База данных создана успешно!")
print("Данные в таблице:")
for row in results:
    print(f"ID: {row[0]}, Имя: {row[1]}, Город: {row[2]}")

conn.close()