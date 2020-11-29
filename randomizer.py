import random


def randomize_entity(db):
    """Рандомное изменение данных в таблицах в БД.

    Args:
        db: DataBase-объект, в котором произовдить замену
    """
    objects_to_change = ['hull', 'weapon', 'engine']
    tables = db.get_tables()

    for table in tables:
        if table == 'Ships':

            for ship in db.get_all(table):
                ship_name, ship_weapon, ship_hull, ship_engine = ship

                # Выбираем случайный объект и генерим новое значение
                # Если сгенериться такое же значение - изменение не произойдет
                obj_to_change = random.choice(objects_to_change)
                new_obj = db.get_random_obj(obj_to_change)

                db.update_one(table, ship_name, obj_to_change, new_obj)

        else:
            columns = db.get_columns_name(table)[1:]
            columns_names = [column[1] for column in columns]

            for obj in db.get_all(table):
                # Выбираем случайный объект и генерим новое значение
                # Если сгенериться такое же значение - изменение не произойдет
                obj_to_change = random.choice(columns_names)
                new_obj = random.randint(1, 10)
                obj_name = obj[0]

                db.update_one(table, obj_name, obj_to_change, new_obj)
