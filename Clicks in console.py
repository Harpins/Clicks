import os
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv


SHORTENED_URL_NETLOCS = ['vk.cc']


def shorten_link(token, url):
    parameters = {
        'access_token': token,
        'v': '5.199',
        'url': url,
        'private': 0,
    }
    response = requests.post(
        'https://api.vk.ru/method/utils.getShortLink', data=parameters)
    response.raise_for_status()
    try:
        return response.json()['response']['short_url']
    except KeyError:
        return f'Ошибка АPI {response.json()['error']['error_code']}'
    except Exception as expt:
        return f'Что-то пошло не так: {expt}'


def count_clicks(token, url, access_key, version='5.199', source='vk_cc', interval='forever', intervals_count=1, extended=0):
    if short_or_long(url):
        key = urlparse(url).path[1:]
    else:
        short_link = shorten_link(token, url)
        if not short_link:
            return 'Неверный формат ссылки'
        key = urlparse(short_link).path[1:]

    parameters = {
        'access_token': token,
        'v': version,
        'key': key,
        'source': source,
        'access_key': access_key,
        'interval': interval,
        'intervals_count': intervals_count,
        'extended': extended,
    }
    response = requests.post(
        'https://api.vk.ru/method/utils.getLinkStats', data=parameters, timeout=20)
    response.raise_for_status()
    try:
        return 'Количество переходов по ссылке: ' + str(response.json()['response']['stats'][0]['views'])
    except IndexError:
        return 'Нет доступа к статистике'
    except KeyError:
        return f'Ошибка АPI {response.json()['error']['error_code']}'
    except Exception as expt:
        return f'Что-то пошло не так: {expt}'


def short_or_long(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc in SHORTENED_URL_NETLOCS


def main():
    load_dotenv('APIToken.env')
    service_token = os.getenv('service_token')
    access_key = os.getenv('access_token')
    if not service_token:
        print('Не найден токен')
        exit(1)
    if not access_key:
        print('Не найден ключ доступа')
        exit(1)
    url = str(input('Введите ссылку: '))
    if not short_or_long(url):
        print(shorten_link(service_token, url))
    print(count_clicks(service_token, url, access_key))


if __name__ == '__main__':
    main()
