"""Разные функции, не требующие импортов из других модулей"""

def make_search(k, u):
    """формирует запрос и отдаёт итератор с результатами"""
    sex = make_sex(u['sex'])
    birth_year = make_birth_year(u)
    city = u['city']['id']

    search_params = {'sort': 0,
                     'is_closed': False,
                     'has_photo': 1,
                     'sex': sex,
                     'birth_year': birth_year,
                     'city': city,
                     'status': 1}

    res = k.search(search_params)

    return res


def check_user(u):
    """максимальное огораживаниеи от закрытых профилей и отсутствующих полей"""
    if u['is_closed']:
        return False
    param_list = ['id', 'first_name', 'last_name', 'sex', 'bdate', 'city']
    for ii in param_list:
        if ii not in u.keys():
            return False
    return True

def get_id(url):
    """переспрашивает ссылку на профиль"""
    if url:
        id_ = get_id_from_url(url)
    else:
        url = input('Введите ссылку на пользователя для поиска ему пары:\n')
        id_ = get_id_from_url(url)
    return id_

def get_id_from_url(url: str):
    """разбор ссылки профиля ВК"""
    result = url.strip().split('/id')[-1].split('/')[-1]
    if result:
        output = result
    else:
        output = None  # будет ссылка на свой собственный аккаунт

    return output


def best_size(sizes_list):
    """выбор самой большой фотки по типу"""
    type_ = ['s', 'm', 'x', 'o', 'p', 'q', 'r', 'y', 'z', 'w']
    size_ = range(1, len(type_) + 1)
    sizes_rating = dict(zip(type_, size_))
    top_size = sorted(sizes_list, key=(lambda item: sizes_rating[item['type']]), reverse=True)[0]
    return top_size


def get_best_prof_photos(k, id_):
    """выбирает 3 самых залайканых фотки"""
    r = k.get_prof_photos(id_)
    top_3_links = None
    if 'items' in r.keys():
        res = k.get_prof_photos(id_)['items']
        res.sort(key=lambda item: item['likes']['count'], reverse=True)
        top_3 = res[0: min(3, len(res))]
        top_3_links = [best_size(item['sizes'])['url'] for item in top_3]

    return top_3_links


def make_sex(sex):
    """переспрашивает пол, если он не определён"""
    if sex != 0:
        sex = 3 - sex
    else:
        while sex != 1 or sex != 1:
            sex = int(input('какой пол искать? (1 - женский, 2 - мужской)'))
    return sex


def make_birth_year(u):
    """переспрашивает год рождения, если он не определён"""
    if 'bdate' not in u.keys():
        birth_year = None
        while not (isinstance(birth_year, int) and 1900 < birth_year < 2021):
            birth_year = int(input('Какой год рождения?'))
    elif len(u['bdate'].split('.')) != 3:
        birth_year = None
        while not (isinstance(birth_year, int) and 1900 < birth_year < 2021):
            birth_year = int(input('Какой год рождения?'))
    else:
        birth_year = u['bdate'].split('.')[-1]

    return birth_year

