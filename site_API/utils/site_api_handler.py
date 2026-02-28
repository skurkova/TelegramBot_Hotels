import json
import os

import requests
from loguru import logger

from site_API.core import url_api, headers_get, headers_post
from tg_API.config_data.config import MOCK_API


def load_mock_data(filename: str):
    """Загружает данные из JSON-файла"""
    filepath = os.path.join('mock_data', filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.info(f'Mock-файл не найден: {filepath}')


def api_request(method_endswith, params, method_type):
    # Если MOCK_API=True — возвращает данные из JSON:
    if MOCK_API:
        logger.info('MOCK-режим: используем данные из JSON')

        if '/locations/v3/search' in method_endswith:
            return load_mock_data('possible_cities.json')

        elif '/properties/v2/list' in method_endswith:
            return load_mock_data('possible_hotels.json')

        elif '/properties/v2/detail' in method_endswith:
            return load_mock_data('hotel_options.json')

        else:
            logger.info(f'MOCK-данные отсутствуют: {method_endswith}')

    # РЕАЛЬНЫЙ API
    url = url_api + method_endswith
    if method_type == 'GET':
        return get_request(url=url, params=params)
    elif method_type == 'POST':
        return post_request(url=url, params=params)


def get_request(url, params):
    try:
        response = requests.get(url, headers=headers_get, params=params)
        logger.info(f'Сервер вернул ответ: {response.status_code}')
        if response.status_code == requests.codes.ok:
            return response.json()
        elif response.status_code == 451:
            raise Exception(f'API недоступен в вашем регионе, статус кода {response.status_code}')
        else:
            raise Exception(f'Запрос пуст, статус кода {response.status_code}')
    except Exception:
        logger.info(Exception)
        raise


def post_request(url, params):
    try:
        response = requests.post(url, json=params, headers=headers_post)
        logger.info(f'Сервер вернул ответ: {response.status_code}')
        if response.status_code == requests.codes.ok:
            return response.json()
        elif response.status_code == 451:
            raise Exception(f'API недоступен в вашем регионе, статус кода {response.status_code}')
        else:
            raise Exception(f'Запрос пуст, статус кода {response.status_code}')
    except Exception:
        logger.info(Exception)
        raise
