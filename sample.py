import requests

ENDPOINT = "http://example.com/"


class Sample:
    def hoge(self, arg1: int, arg2: int):
        return arg1 + arg2


def get_weather_reports() -> dict:
    res = requests.get(ENDPOINT + "/weather_reports")
    if res.status_code == 200:
        return res.json()
    return None
