import requests
from loguru import logger

from site_API.core import url_api, headers_get, headers_post


def api_request(method_endswith, params, method_type):
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
            logger.error('⚠️ API заблокирован (HTTP 451). Включите USE_MOCK_API=True в .env')
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
            logger.error('⚠️ API заблокирован (HTTP 451). Включите USE_MOCK_API=True в .env')
            raise Exception(f'API недоступен в вашем регионе, статус кода {response.status_code}')
        else:
            raise Exception(f'Запрос пуст, статус кода {response.status_code}')
    except Exception:
        logger.info(Exception)
        raise
