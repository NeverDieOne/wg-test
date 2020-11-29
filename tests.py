from db import DataBase
import os
from dotenv import load_dotenv
from randomizer import randomize_entity


def make_message(name, object_, current, dumped):
    """Вспомогательная функция для генерации сообщения к assert"""
    return f'{name}, {object_}\n\texpected {dumped}, was {current}'


def setup():
    load_dotenv()

    # Создаем БД и забиваем данынми
    start_db = DataBase(os.getenv('DB_NAME'))
    start_db.create_all()
    start_db.fill_all()

    # Делаем дамп с которым будем сравнивать
    dumped_db = start_db.dump_db(os.getenv('DB_DUMP_NAME'))

    # Random changes in DB
    randomize_entity(start_db)


def teardown():
    os.remove(os.getenv('DB_DUMP_NAME'))
    os.remove(os.getenv('DB_NAME'))


def test_ships():
    """Функция-генератор для проверки всех кораблей"""
    current_db = DataBase(os.getenv('DB_NAME'))
    dumped_db = DataBase(os.getenv('DB_DUMP_NAME'))

    for ship in current_db.get_all('Ships'):
        # Получаем текущие значения
        ship_name, ship_weapon, ship_hull, ship_engine = ship

        # Получаем значения из дампа
        dumped_ship = dumped_db.get_one('Ships', ship[0])
        dumped_name, dumped_weapon, dumped_hull, dumped_engine = dumped_ship

        yield check_weapon, ship_name, ship_weapon, dumped_weapon
        yield check_hull, ship_name, ship_hull, dumped_hull
        yield check_engine, ship_name, ship_engine, dumped_engine


def check_weapon(ship_name, current_weapon, dumped_weapon):
    """Проверка орудий корабля"""
    current_db = DataBase(os.getenv('DB_NAME'))
    dumped_db = DataBase(os.getenv('DB_DUMP_NAME'))

    check_values(current_db, dumped_db, 'Weapons', ship_name, current_weapon, dumped_weapon)
    assert current_weapon == dumped_weapon, make_message(ship_name, current_weapon, current_weapon, dumped_weapon)


def check_hull(ship_name, current_hull, dumped_hull):
    """Проверка корпусов корабля"""
    current_db = DataBase(os.getenv('DB_NAME'))
    dumped_db = DataBase(os.getenv('DB_DUMP_NAME'))

    check_values(current_db, dumped_db, 'Hulls', ship_name, current_hull, dumped_hull)
    assert current_hull == dumped_hull, make_message(ship_name, current_hull, current_hull, dumped_hull)


def check_engine(ship_name, current_engine, dumped_engine):
    """Проверка двигателей корабля"""
    current_db = DataBase(os.getenv('DB_NAME'))
    dumped_db = DataBase(os.getenv('DB_DUMP_NAME'))

    check_values(current_db, dumped_db, 'Engines', ship_name, current_engine, dumped_engine)
    assert current_engine == dumped_engine, make_message(ship_name, current_engine, current_engine, dumped_engine)


def check_values(current_db, dumped_db, table_name, ship_name, current_obj, dumped_obj):
    """Проверка значений сущности"""
    columns_name = [obj[1] for obj in current_db.get_columns_name(table_name)]

    if current_obj == dumped_obj:
        current_value = current_db.get_one(table_name, current_obj)
        dumped_value = dumped_db.get_one(table_name, dumped_obj)

        for raw in zip(columns_name, current_value, dumped_value):
            name, current, dumped = raw
            assert current == dumped, make_message(ship_name, name, current, dumped)
