import requests
from bs4 import BeautifulSoup
import fake_useragent
from IPython.display import display
import pandas as pd


# Функция для запросов
def fetch_data(url):
    response = requests.get(url, headers={"user-agent": fake_useragent.UserAgent().random})
    response.raise_for_status()
    return response.content


# Функция для анализа response.content
def analyze_response_content(content):
    soup = BeautifulSoup(content, "lxml")

    existence_section_box = (soup
                             .find("div", attrs={"class": "section-group section-group--gap-medium"})
                             .find("div", attrs={"class": "section-group section-group--gap-medium"})
                             )
    if existence_section_box is not None:
        all_vacancy_in_page = existence_section_box.find_all("div", attrs={"class": "section-box"})
        vacancies_count = len([i for i in all_vacancy_in_page if i])
    else:
        vacancies_count = 0

    existence_pagination = (soup
                            .find("div", attrs={"class": "section-group section-group--gap-medium"})
                            .find("div", attrs={"class": "section-group section-group--gap-medium"})
                            )
    if existence_pagination is not None:
        pagination = existence_pagination.find("div", attrs={"class": "paginator"})
    else:
        pagination = None

    if pagination is not None:
        next_url_in_soup = pagination.find("div", attrs={"class": "pagination"}).find("a", attrs={"rel": "next"})
        next_url = next_url_in_soup.attrs['href'] if next_url_in_soup else None
    else:
        next_url = None
    return {
        'vacancies_count': vacancies_count,
        'next_url': next_url
    }


# Функция сбора всех вакансий
def gather_all_vacancies(first_url):
    base_url = f'https://career.habr.com'
    vacancies_count = 0
    next_url = first_url
    while next_url is not None:
        content = fetch_data(base_url + next_url)
        data = analyze_response_content(content)
        vacancies_count += data.get('vacancies_count')
        next_url = data.get('next_url')
    return vacancies_count


# Подготовка данных для итогового вывода в виде таблицы
region_list = []
text_list = []
skill_level_list = []
vacancy_count_by_skill_list = []
table_data = {'Регион': region_list,
              'Текст поиска': text_list,
              'Уровень скилла': skill_level_list,
              'Количество вакансий': vacancy_count_by_skill_list}

# Входые данные:
# Указание соответствия уровня скилла в url
skill_level = {
    "Junior": "3",
    "Middle": "4",
    "Senior": "5"
}

# Выражение для поиска
text = [
    'Аналитика данных',
    'Data Science'
]

# Регионы для поиска
regions = {
    "Нижний Новгород": "c_715",
    "Москва": "c_678"
}

# Подсчёт всех вакансий в соответствии с запросом из text
for rk, rv in regions.items():
    for item in text:
        # Счётчик вакансий для каждого уровня скилла
        vacancy_count_by_skill = {
            "Junior": 0,
            "Middle": 0,
            "Senior": 0
        }
        for k, v in skill_level.items():
            count = gather_all_vacancies(f'/vacancies?locations[]={rv}'
                                         f'&page=1&q={text[text.index(item)]}&qid={v}&type=all')
            # Сбор данных в таблицу
            region_list.append(rk)
            text_list.append(item)
            skill_level_list.append(k)
            vacancy_count_by_skill_list.append(count)

# Вывод таблицы
table = pd.DataFrame(table_data)
display(table)
