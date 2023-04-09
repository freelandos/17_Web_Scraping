import re
import json

import requests
from fake_headers import Headers
from bs4 import BeautifulSoup


def get_html_data(search_text, city_list, page):
    url = 'https://hh.ru/search/vacancy'
    params = {
        'text': search_text,
        'area': city_list,
        'page': page,
        'items_on_page': 20,
        'customDomain': 1
    }
    headers = Headers(browser='firefox', os='win')
    html_data = requests.get(url, params=params, headers=headers.generate()).text
    return html_data


def get_vacancy_cards(html_data):
    soup = BeautifulSoup(html_data, 'lxml')
    tag_div_cards = soup.find('div', id='a11y-main-content')
    cards = tag_div_cards.find_all('div', class_='serp-item')
    return cards


def get_vacancy_title(vacancy_card):
    tag_a_vacancy = vacancy_card.find('a', class_='serp-item__title')
    title = re.sub(r'\s+', ' ', tag_a_vacancy.text).strip()
    return title


def get_vacancy_url(vacancy_card):
    tag_a_vacancy = vacancy_card.find('a', class_='serp-item__title')
    url = tag_a_vacancy['href']
    return url


def get_vacancy_salary(vacancy_card):
    tag_span_salary = vacancy_card.find('span', class_='bloko-header-section-3')
    if tag_span_salary:
        salary = re.sub(r'\s+', ' ', tag_span_salary.text)
        return salary
    return 'не указана'


def get_vacancy_company(vacancy_card):
    tag_div_company = vacancy_card.find('div', class_='vacancy-serp-item__meta-info-company')
    company = re.sub(r'\s+', ' ', tag_div_company.text).strip()
    return company


def get_vacancy_city(vacancy_card):
    tag_div_city = vacancy_card.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
    city_station = tag_div_city.text
    city = city_station.split(',')[0]
    return city


def get_parsed_data(vacancy_cards):
    parsed_data = []
    for vacancy_card in vacancy_cards:
        title = get_vacancy_title(vacancy_card)
        url = get_vacancy_url(vacancy_card)
        salary = get_vacancy_salary(vacancy_card)
        company = get_vacancy_company(vacancy_card)
        city = get_vacancy_city(vacancy_card)
        data = {
            'vacancy': title,
            'url': url,
            'salary': salary,
            'company': company,
            'city': city
        }
        parsed_data.append(data)
    return parsed_data


def get_parsed_data_usd(vacancy_cards):
    parsed_data_usd = []
    for vacancy_card in vacancy_cards:
        salary = get_vacancy_salary(vacancy_card)
        if re.search(r'[USDusd]+', salary):
            title = get_vacancy_title(vacancy_card)
            url = get_vacancy_url(vacancy_card)
            company = get_vacancy_company(vacancy_card)
            city = get_vacancy_city(vacancy_card)
            data = {
                'vacancy': title,
                'url': url,
                'salary': salary,
                'company': company,
                'city': city
            }
            parsed_data_usd.append(data)
    return parsed_data_usd


def create_json_file(data, pc_file_path):
    with open(pc_file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    search_text = 'python django flask'
    city_list = [1, 2]

    parsed_data_total = []
    parsed_data_total_usd = []
    page = -1
    while True:
        page += 1
        html_data = get_html_data(search_text, city_list, page)
        vacancy_cards = get_vacancy_cards(html_data)
        if vacancy_cards:
            parsed_data = get_parsed_data(vacancy_cards)
            parsed_data_usd = get_parsed_data_usd(vacancy_cards)
            parsed_data_total += parsed_data
            parsed_data_total_usd += parsed_data_usd
        else:
            break

    create_json_file(parsed_data_total, 'parsed_data.json')
    create_json_file(parsed_data_total_usd, 'parsed_data_usd.json')
