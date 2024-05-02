import sqlite3
import os
import cv2
import math


def create_db_connection():
    conn = sqlite3.connect('crawled_data.db')
    return conn


def create_table(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS images")
        cursor.execute('''CREATE TABLE IF NOT EXISTS images (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            data BLOB)''')
        conn.commit()
    except Exception as e:
        print(f"Error in initialize_database: {str(e)}")
    finally:
        cursor.close()


def read_photo(conn):
    cursor = conn.cursor()
    image_folder = 'photos/'

    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith('.jpg'):
            with open(image_folder + filename, 'rb') as f:
                image = f.read()
            cursor.execute('''INSERT INTO images (name, data) VALUES (?, ?)''', (filename, image))
            conn.commit()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    conn = create_db_connection()
    create_table(conn)
    read_photo(conn)
