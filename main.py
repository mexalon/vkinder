import json

import sqlalchemy

from functions import *
from models import User, ProfUrls, create_db
from secret import my_token, comm_token, DSN
from vk_class import Kinder, Talk


def search_result_processing(id_, t, k, session_maker):
    # по айти запрашивает полный профиль, и если он валидный, то добавляет в базу и выводит результат

    if Session:
        # если есть доступ к базе - запрос, чтобы избежать повтор
        already_in_db = session_maker().query(User).filter(User.user_id == id_).first()
    else:
        already_in_db = False

    if not already_in_db:  # если такого нет в базе - добавляем в базу
        raw_u = k.users_get(id_)[0]  # полный профиль из результатов поиска
        if check_user(raw_u):
            # новый объект профиля
            new_u = User(user_id=raw_u['id'],
                         first_name=raw_u['first_name'],
                         last_name=raw_u['last_name'],
                         sex=raw_u['sex'],
                         bdate=raw_u['bdate'],
                         city=raw_u['city']['title'])

            # новый объект фоток
            pu = [ProfUrls(user_id=new_u.user_id, url=one_url) for one_url in get_best_prof_photos(k, new_u.user_id)]
            # запись в базу
            if Session:
                session = session_maker()
                session.add(new_u)
                for p in pu:
                    session.add(p)
                session.commit()
            else:  # запись в файл если недоступна база
                with open("dump_file.txt", "a", encoding='utf-8') as f:
                    f.write(new_u.mk_dict().__repr__())
                    # я думал выгрузить словарь в виде json, но там кириллица отображается  ввиде кодов юникода
                    # типа \u0430 И я ничего не могу с этим поделать. В каком вообще виде лучше всего хранить обьекты
                    # алхимии, если не в виде базы?
                with open("dump_file.json", "a", encoding='utf-8') as f:
                    json.dump(new_u.mk_dict(), f)

            print(f"Вот, например, {new_u}")  # вывод результатов в консоль
            [print(item) for item in pu]

            t.write(f"Вот, например, {new_u}")  # вывод результатов в чат
            [t.write(item) for item in pu]
            return True

        else:
            return False  # профиль не валидный
    return False


def go_go(k, session_maker):
    hi = k.read_msg()
    new_client = hi.user_id
    t = Talk(k, new_client)
    t.write('Привет!')

    resp = k.users_get(new_client)  # профиль пользователя, которому надо найти пару

    u = resp[0]
    t.write(f"Ищем пару для {u['first_name']} {u['last_name']}")
    res = make_search(k, u, t)  # итератор с результатами поиска
    for r in res:
        new_id = search_result_processing(r['id'], t, k, session_maker)  # обработка и добавление в базу
        if not new_id:  # невалидный результат - пробуем следующий
            continue
        else:
            t.write(f"Выберите 'q' для выхода или 'n' для продолжения")
            q = t.read()
            if q == 'q':
                t.write(f"Пока, {u['first_name']} {u['last_name']}!")
                return


if __name__ == '__main__':
    try:
        Session = create_db(DSN)
    except sqlalchemy.exc.OperationalError as error_msg:
        print(error_msg)
        Session = False

    kinder = Kinder(token=my_token, c_token=comm_token)
    go_go(kinder, Session)
