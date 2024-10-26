import os
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv


def shorten_link(token, url):
    parameters = {
        'access_token': token,
        'v': '5.199',
        'url': url,
        'private': 0,
    }
    response = requests.post(
        'https://api.vk.ru/method/utils.getShortLink', data=parameters, timeout=20)
    response.raise_for_status()
    response_data = response.json()
    if 'response' in response_data:
        return response_data['response']['short_url']
    elif 'error' in response_data:
        return f'Ошибка API {response_data['error']['error_code']}'


def get_url_key(token, url):
    if is_short_or_long(url):
        return urlparse(url).path[1:]
    else:
        short_link = shorten_link(token, url)
        return urlparse(short_link).path[1:]


def count_clicks(token, url):
    key = get_url_key(token, url)
    parameters = {
        'access_token': token,
        'v': '5.199',
        'key': key,
        'source': 'vk_cc',
        'access_key': '',
        'interval': 'forever',
        'intervals_count': 1,
        'extended': 0,
    }
    response = requests.post(
        'https://api.vk.ru/method/utils.getLinkStats', data=parameters, timeout=20)
    response.raise_for_status()
    response_data = response.json()
    if 'response' in response_data:
        if response_data['response']['stats']:
            return f'Количество переходов по ссылке: {response_data['response']['stats'][0]['views']}'
        else:
            return 'Нет доступа к статистике'
    elif 'error' in response_data:
        return f'Ошибка API {response_data['error']['error_code']}'


def is_short_or_long(url):
    shortened_url_netlocs = ['vk.cc']
    parsed_url = urlparse(url)
    return parsed_url.netloc in shortened_url_netlocs


def main():
    load_dotenv('APIToken.env')
    vk_service_token = os.getenv('VK_SERVICE_TOKEN')
    if not vk_service_token:
        print('Не найден токен')
        return
    url = input('Введите ссылку: ')
    try:
        if not is_short_or_long(url):
            print(shorten_link(vk_service_token, url))
        print(count_clicks(vk_service_token, url))
    except requests.exceptions.HTTPError as error:
        print(f'Ошибка HTTP {error.response.status_code}')


if __name__ == '__main__':
    main()
