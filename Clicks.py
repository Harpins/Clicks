import os
import argparse
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
    clicks_data = 'неизвестно'
    if response_data['response']['stats']:
        clicks_data = response_data['response']['stats'][0]['views']
    return clicks_data


def is_shorten_link(token, url):
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        url = f'http://{url}'
        parsed_url = urlparse(url)
    parameters = {
        'url': url,
        'access_token': token,
        'v': '5.199',
    }
    response = requests.post(
        'https://api.vk.ru/method/utils.checkLink', data=parameters, timeout=20)
    response.raise_for_status()
    response_data = response.json()
    if 'error' in response_data:
        raise Exception(f'Ошибка API {response_data['error']['error_code']}')
    shortened_url_netlocs = ['vk.cc']
    parsed_url_netloc = parsed_url.netloc
    parsed_url_path = parsed_url.path[1:]
    is_short = parsed_url_netloc in shortened_url_netlocs
    if is_short and not parsed_url_path:
        raise Exception('Неверный формат ссылки')
    return is_short


def main():
    parser = argparse.ArgumentParser(
        description='Ввод ссылки'
    )
    parser.add_argument('link', help='Введите ссылку', type=str)
    args = parser.parse_args()

    load_dotenv('APIToken.env')
    vk_service_token = os.environ['VK_SERVICE_TOKEN']
    url = args.link
    
    try:
        if not is_shorten_link(vk_service_token, url):
            short_link = shorten_link(vk_service_token, url)
            print(short_link)
        else:
            link_key = urlparse(url).path[1:]
            print(f'Количество переходов по ссылке: {
                  count_clicks(vk_service_token, link_key)}')
    except requests.exceptions.HTTPError as error:
        print(f'Ошибка HTTP {error.response.status_code}')


if __name__ == '__main__':
    main()
