from secret import token, DSN
from vk_class import Kinder
from functions import *
from models import User, ProfUrls, create_db, clear_db

def serch_result_processing(r, k, Session):
    raw_u = k.users_get(r['id'])[0]  # какой то профиль из результатов поиска
    session = Session()
    if check_user(raw_u):
        # новый объект профиля
        new_u = User(user_id=raw_u['id'],
                     first_name=raw_u['first_name'],
                     last_name=raw_u['last_name'],
                     sex=raw_u['sex'],
                     bdate=raw_u['bdate'],
                     city=raw_u['city']['title'])

        already_in_db = session.query(User).filter(User.user_id == new_u.user_id).first()
        if not already_in_db:  # если такого нет в базе - добавляем в базу
            session.add(new_u)
            for prof_url in get_best_prof_photos(k, r['id']):
                pu = ProfUrls(user_id=r['id'], url=prof_url)
                session.add(pu)

            session.commit()

        session = Session()
        new_u_from_db = session.query(User).filter(User.user_id == new_u.user_id).first()
        prof_photo_from_db = new_u_from_db.photo_urls

        print(f"Вот, например, {new_u_from_db}")
        [print(item) for item in prof_photo_from_db]

        result = True
    else:
        result = False

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
        if not serch_result_processing(r, k, Session):  # валидность результата
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


