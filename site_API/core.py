from tg_API.config_data.config import RAPID_API_KEY, RAPID_API_HOST


url_api = "https://" + RAPID_API_HOST


headers_get = {
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": RAPID_API_HOST
}

headers_post = {
    "content-type": "application/json",
    "X-RapidAPI-Key": RAPID_API_KEY,
    "X-RapidAPI-Host": RAPID_API_HOST}
