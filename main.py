from functions import *
from models import User, ProfUrls, create_db, clear_db
from secret import token, DSN
from vk_class import Kinder


def search_result_processing(id_, k, Session):
    # по айти запрашивает полный профиль, и если он валидный, то добавляет в базу и выводит результат
    already_in_db = Session().query(User).filter(User.user_id == id_).first()

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

            session = Session()
            session.add(new_u)
            for prof_url in get_best_prof_photos(k, new_u.user_id):
                pu = ProfUrls(user_id=new_u.user_id, url=prof_url)
                session.add(pu)
            session.commit()
        else:
            return False  # профиль не валидный

    # запрос из базы, чтобы лучше научиться
    new_u_from_db = Session().query(User).filter(User.user_id == id_).first()
    prof_photo_from_db = new_u_from_db.photo_urls

    print(f"Вот, например, {new_u_from_db}") #вывод результатов
    [print(item) for item in prof_photo_from_db]

    result = new_u_from_db.id # возвращает айди пользователя в собственной базе
    return result

def go_go(k, Session, url=None):
    id_ = get_id(url) # айди из ссылки на профиль либо запрос профиля
    resp = k.users_get(id_) # профиль пользователя, которому надо найти пару

    if not resp:
        print('неправильная ссылка')
        return
    else:
        u = resp[0]

    res = make_search(k, u)  # итератор с результатами поиска


    print(f"Ищем пару для {u['first_name']} {u['last_name']}")
    for r in res:
        new_id = search_result_processing(r['id'], k, Session) # обработка и добавление в базу
        if not new_id:  # невалидный результат - пробуем следующий
            continue
        else:
            print(f"Выберите q для выхода или Энтер для продолжения")
            q = input()
            if q == 'q':
                return

if __name__ == '__main__':
    Session = create_db(DSN)
    kinder = Kinder(token=token)
    go_go(kinder, Session)



