import os.path
import requests
# noinspection PyUnresolvedReferences,PyPackageRequirements
from twocaptcha import TwoCaptcha

from helpers import _err
from helpers import _log

API_KEY = '47bda1e16c81d8db3d36e9af0bc79b1f'


class Solver:
    CONFIG = {
        'apiKey': API_KEY,
        'pollingInterval': 5,
    }

    def __init__(self):
        self.api = TwoCaptcha(**Solver.CONFIG)

    # @classmethod
    # def __new__(cls, *args, **kwargs):
    #     return TwoCaptcha(**Solver.CONFIG)


def test():
    url = 'https://www.citilink.ru/captcha/image/427fd96bd668272a25003cabd075cdd9/?_=1610653065'
    response = requests.get(url=url)
    if not response.status_code == 200:
        _err(f'Bad response: {response.status_code, response.text}')
        return
    base_dir = os.path.dirname(__file__)
    save_path = os.path.join(base_dir, 'captcha_tests/image.jpeg')
    with open(save_path, 'wb') as file:
        file.write(response.content)
        _log(f'Saved content to file: {save_path}')


if __name__ == '__main__':
    base_dir = os.path.dirname(__file__)
    image_path = os.path.join(base_dir, 'captcha_tests/image.jpeg')
    solver = Solver()
    result = solver.api.normal(image_path, caseSensitive=1)
    print(result)
    print(type(result))
    # _id = '65770696464'
    # result = solver.api.get_result(_id)
    # solver.api.report(_id, False)
