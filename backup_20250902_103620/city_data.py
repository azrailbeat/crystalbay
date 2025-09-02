"""
Real city data for Crystal Bay Travel system
Contains authentic Russian departure cities and international destinations
"""

def get_real_departure_cities():
    """Get list of real Russian cities for international tour departures"""
    return [
        {'id': 1, 'name': 'Москва', 'region': 'Московская область', 'selected': 1},
        {'id': 2, 'name': 'Санкт-Петербург', 'region': 'Ленинградская область', 'selected': 0},
        {'id': 3, 'name': 'Екатеринбург', 'region': 'Свердловская область', 'selected': 0},
        {'id': 4, 'name': 'Новосибирск', 'region': 'Новосибирская область', 'selected': 0},
        {'id': 5, 'name': 'Казань', 'region': 'Республика Татарстан', 'selected': 0},
        {'id': 6, 'name': 'Нижний Новгород', 'region': 'Нижегородская область', 'selected': 0},
        {'id': 7, 'name': 'Челябинск', 'region': 'Челябинская область', 'selected': 0},
        {'id': 8, 'name': 'Самара', 'region': 'Самарская область', 'selected': 0},
        {'id': 9, 'name': 'Омск', 'region': 'Омская область', 'selected': 0},
        {'id': 10, 'name': 'Ростов-на-Дону', 'region': 'Ростовская область', 'selected': 0},
        {'id': 11, 'name': 'Уфа', 'region': 'Республика Башкортостан', 'selected': 0},
        {'id': 12, 'name': 'Красноярск', 'region': 'Красноярский край', 'selected': 0},
        {'id': 13, 'name': 'Воронеж', 'region': 'Воронежская область', 'selected': 0},
        {'id': 14, 'name': 'Пермь', 'region': 'Пермский край', 'selected': 0},
        {'id': 15, 'name': 'Волгоград', 'region': 'Волгоградская область', 'selected': 0},
        {'id': 16, 'name': 'Краснодар', 'region': 'Краснодарский край', 'selected': 0},
        {'id': 17, 'name': 'Тюмень', 'region': 'Тюменская область', 'selected': 0},
        {'id': 18, 'name': 'Иркутск', 'region': 'Иркутская область', 'selected': 0}
    ]

def get_real_destinations():
    """Get list of real international travel destinations"""
    return [
        {'id': 1934, 'name': 'Нячанг, Вьетнам', 'town_key': 1934, 'country': 'Вьетнам'},
        {'id': 4533, 'name': 'Дананг, Вьетнам', 'town_key': 4533, 'country': 'Вьетнам'},
        {'id': 2009, 'name': 'Хошимин, Вьетнам', 'town_key': 2009, 'country': 'Вьетнам'},
        {'id': 1192, 'name': 'Пхукет, Таиланд', 'town_key': 1192, 'country': 'Таиланд'},
        {'id': 1454, 'name': 'Патонг, Таиланд', 'town_key': 1454, 'country': 'Таиланд'},
        {'id': 1338, 'name': 'Пхукет Центр, Таиланд', 'town_key': 1338, 'country': 'Таиланд'},
        {'id': 1784, 'name': 'Семиньяк, Бали', 'town_key': 1784, 'country': 'Индонезия'},
        {'id': 1786, 'name': 'Кута, Бали', 'town_key': 1786, 'country': 'Индонезия'},
        {'id': 2006, 'name': 'Фукуок, Вьетнам', 'town_key': 2006, 'country': 'Вьетнам'},
        {'id': 1935, 'name': 'Камрань, Вьетнам', 'town_key': 1935, 'country': 'Вьетнам'}
    ]