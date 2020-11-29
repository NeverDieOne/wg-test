import sqlite3
import argparse
import os
from dotenv import load_dotenv
import random
import shutil


def get_arguments():
    parser = argparse.ArgumentParser(description='Файл для работы с БД')
    parser.add_argument('-c', '--create_db', action='store_true',
                        help='Создаст базу данных с необходимой структурой')
    parser.add_argument('-f', '--fill_db', action='store_true',
                        help='Наполнит базу данных тестовыми данными')

    return parser.parse_args()


class DataBase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def __del__(self):
        self.connection.close()
        self.connection = None

    def get_database(self):
        """Получение коннекта к БД.

        Если объект уже существует, будет возвращен он.
        """
        if not self.connection:
            conn = sqlite3.connect(self.db_path)
            return conn

        return self.connection

    def create_ships_table(self):
        """Создание таблицы кораблей"""
        cursor = self.get_database().cursor()

        cursor.execute("""CREATE TABLE Ships 
            (ship TEXT PRIMARY KEY,
            weapon TEXT NOT NULL,
            hull TEXT NOT NULL,
            engine TEXT NOT NULL,
            FOREIGN KEY (hull) REFERENCES Hulls(hull),
            FOREIGN KEY (weapon) REFERENCES Weapons(weapon),
            FOREIGN KEY (engine) REFERENCES Engines(engine))
        """)

    def create_weapons_table(self):
        """Создание таблицы орудий"""
        cursor = self.get_database().cursor()

        cursor.execute("""CREATE TABLE Weapons
            (weapon TEXT PRIMARY KEY,
            reload_speed INTEGER NOT NULL,
            rotational_speed INTEGER NOT NULL,
            diameter INTEGER NOT NULL,
            power_volley INTEGER NOT NULL,
            count INTEGER NOT NULL)
        """)

    def create_hulls_table(self):
        """Создание таблицы корпусов"""
        cursor = self.get_database().cursor()

        cursor.execute("""CREATE TABLE Hulls
            (hull TEXT PRIMARY KEY,
            armor INTEGER NOT NULL,
            type INTEGER NOT NULL,
            capacity INTEGER NOT NULL)
        """)

    def create_engines_table(self):
        """Создание таблицы двигателей"""
        cursor = self.get_database().cursor()

        cursor.execute("""CREATE TABLE Engines
            (engine TEXT PRIMARY KEY,
            power INTEGER NOT NULL,
            type INTEGER NOT NULL)
        """)

    def fill_weapons(self, count=20):
        """Заполнение таблицы орудия.

        Args:
            count (int): количество объектов для создания
        """
        connection = self.get_database()
        cursor = connection.cursor()

        for _ in range(count):
            weapon = f"weapon-{_}"
            reload_speed = random.randint(1, 10)
            rotation_speed = random.randint(1, 10)
            diameter = random.randint(1, 10)
            power_volley = random.randint(1, 10)
            count = random.randint(1, 10)

            cursor.execute("INSERT INTO Weapons VALUES (?, ?, ?, ?, ?, ?)",
                           (weapon, reload_speed, rotation_speed, diameter, power_volley, count))

        connection.commit()

    def fill_hulls(self, count=5):
        """Заполнение таблицы корпусов.

        Args:
            count (int): количество объектов для создания
        """
        connection = self.get_database()
        cursor = connection.cursor()

        for _ in range(count):
            hull = f"hull-{_}"
            armor = random.randint(1, 10)
            type_ = random.randint(1, 10)
            capacity = random.randint(1, 10)

            cursor.execute("INSERT INTO Hulls VALUES (?, ?, ?, ?)",
                           (hull, armor, type_, capacity))

        connection.commit()

    def fill_engines(self, count=6):
        """Заполнение таблицы двигателей.

        Args:
            count (int): количество объектов для создания
        """
        connection = self.get_database()
        cursor = connection.cursor()

        for _ in range(count):
            engine = f"engine-{_}"
            power = random.randint(1, 10)
            type_ = random.randint(1, 10)

            cursor.execute("INSERT INTO Engines VALUES (?, ?, ?)",
                           (engine, power, type_))

        connection.commit()

    def fill_ships(self, count=200):
        """Заполнение таблицы кораблей.

        Args:
            count (int): количество объектов для создания
        """
        connection = self.get_database()
        cursor = connection.cursor()

        for _ in range(count):
            ship = f"ship-{_}"
            hull = self.get_random_obj('hull')
            engine = self.get_random_obj('engine')
            weapon = self.get_random_obj('weapon')

            cursor.execute("INSERT INTO Ships VALUES (?, ?, ?, ?)",
                           (ship, weapon, hull, engine))

        connection.commit()

    def get_all(self, table_name):
        """Получение всех объектов из таблицы.

        Args:
            table_name (str): имя таблицы в БД
        """
        cursor = self.get_database().cursor()

        cursor.execute(f'SELECT * FROM {table_name}')
        return cursor.fetchall()

    def get_one(self, table_name, obj_name):
        """Получение одного объекта из таблицы.

        Args:
            table_name (str): имя таблицы в БД
            obj_name (str): идентификатор объекта
        """
        cursor = self.get_database().cursor()

        entity = table_name[:-1].lower()
        cursor.execute(f"SELECT * FROM {table_name} WHERE {entity}='{obj_name}'")
        return cursor.fetchone()

    def update_one(self, table_name, obj_name, value_entity, value):
        """Обновление одного объекта в таблице.

        Args:
            table_name (str): имя таблицы в БД
            obj_name (str): идентификатор объекта
            value_entity (str): изменяемое значение
            value (str): новое значение
        """
        connection = self.get_database()
        cursor = connection.cursor()
        entity = table_name.lower()[:-1]

        cursor.execute(f"UPDATE {table_name} SET {value_entity}='{value}' WHERE {entity}='{obj_name}'")

        connection.commit()

    def get_random_obj(self, obj_name):
        """Получение случайного объекта из таблицы.

        Args:
            obj_name (str): имя объекта (weapon, hull, engine)
        """
        cursor = self.get_database().cursor()

        # Генерируем имя таблицы из объекта
        table_name = f"{obj_name.capitalize()}s"

        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        obj_count = cursor.fetchone()[0]

        random_number = random.randint(0, obj_count - 1)

        return f'{obj_name}-{random_number}'

    def get_tables(self):
        """Получение имен всех таблиц в БД"""
        cursor = self.get_database().cursor()

        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        return [name[0] for name in cursor.fetchall()]

    def get_columns_name(self, table_name):
        """Получение имен колонок в таблице.

        Args:
            table_name (str): имя таблицы
        """
        cursor = self.get_database().cursor()

        cursor.execute(f'PRAGMA table_info({table_name})')
        return cursor.fetchall()

    def dump_db(self, name):
        """Сделать dump БД.

        Args:
            name (str): имя дампа
        """
        shutil.copy(self.db_path, name)
        return DataBase(name)

    def create_all(self):
        """Создание всех таблиц"""
        self.create_weapons_table()
        self.create_hulls_table()
        self.create_engines_table()
        self.create_ships_table()

    def fill_all(self):
        """Заполнение всех таблиц"""
        self.fill_weapons()
        self.fill_hulls()
        self.fill_engines()
        self.fill_ships()


def main():
    load_dotenv()
    db_path = os.getenv('DB_NAME')
    db = DataBase(db_path)

    args = get_arguments()

    if args.create_db:
        db.create_all()

    if args.fill_db:
        db.fill_all()


if __name__ == '__main__':
    main()
