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
        raise Exception(f'Ошибка API {response_data['error']['error_code']}')


def count_clicks(token, link_key):
    parameters = {
        'access_token': token,
        'v': '5.199',
        'key': link_key,
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
    clicks_data = ''
    if 'response' in response_data and 'stats' in response_data['response']:
        clicks_data = f'Количество переходов по ссылке: {
            response_data['response']['stats'][0]['views']}'
    if 'response' in response_data and not 'stats' in response_data['response']:
        clicks_data = 'Нет доступа к статистике'
    elif 'error' in response_data:
        raise Exception(f'Ошибка API {response_data['error']['error_code']}')
    return clicks_data


def is_short_or_long(url):
    shortened_url_netlocs = ['vk.cc']
    parsed_url = urlparse(url)
    return parsed_url.netloc in shortened_url_netlocs


def main():
    load_dotenv('APIToken.env')
    vk_service_token = os.environ['VK_SERVICE_TOKEN']
    url = input('Введите ссылку: ')
    try:
        if not is_short_or_long(url):
            short_link = shorten_link(vk_service_token, url)
            link_key = urlparse(short_link).path[1:]
            print(short_link)
        else:
            link_key = urlparse(url).path[1:]
        print(count_clicks(vk_service_token, link_key))
    except requests.exceptions.HTTPError as error:
        print(f'Ошибка HTTP {error.response.status_code}')


if __name__ == '__main__':
    main()
