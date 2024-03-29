import time
import os
import os.path
# import requests
# noinspection PyUnresolvedReferences,PyPackageRequirements
from twocaptcha import TwoCaptcha
# noinspection PyPackageRequirements
from twocaptcha import SolverExceptions
# noinspection PyPackageRequirements
from twocaptcha import ValidationException
# noinspection PyPackageRequirements
from twocaptcha import NetworkException
# noinspection PyPackageRequirements
from twocaptcha import ApiException
# noinspection PyPackageRequirements
from twocaptcha import TimeoutException

from .helpers import _err
from .helpers import _log

API_KEY = '47bda1e16c81d8db3d36e9af0bc79b1f'
DEFAULT_TIMEOUT = 120
SLEEP_PAUSE = 5


class Solver:
    CONFIG = {
        'apiKey': API_KEY,
        'pollingInterval': 5,
        'defaultTimeout': DEFAULT_TIMEOUT,
    }

    def __init__(self, ):
        self.api = TwoCaptcha(**Solver.CONFIG)
        self.result = None

    @staticmethod
    def _exc(err):
        return f'{_err.__class__.__name__}: {err}'

    def _error(self, err_msg):
        self.result['error'] = err_msg

    @staticmethod
    def _is_timeout(start_time):
        return time.time() > start_time + DEFAULT_TIMEOUT

    def _delete_tmp_image(self):
        if image_path := self.result.get('image_path'):
            try:
                os.remove(image_path)
            except (FileExistsError, OSError, Exception) as err:
                err_msg = f'Failed to delete captcha tmp image: {image_path}. Error: {self._exc(err)}'
                _err(err_msg)


    def solve(self, image_path, job_id):
        self.result = {
            'image_path': image_path,
            'job_id': job_id,
            'captcha_id': None,
            'code': None,
            'error': None
        }
        if not os.path.exists(image_path):
            err_msg = f'Captcha image file not found for job {job_id}: {image_path}'
            _err(err_msg)
            self._error(err_msg)
            self.result['error'] = err_msg
            return self.result

        start_time = time.time()
        while not self._is_timeout(start_time):
            try:
                result = self.api.normal(image_path, caseSensitive=1)
            except (SolverExceptions, ValidationException, ApiException, Exception) as err:
                self._delete_tmp_image()
                err_msg = f'Captcha API related exception occurred: {self._exc(err)}'
                _err(err_msg)
                self._error(err_msg)
                return self.result
            except (NetworkException, TimeoutException, Exception) as err:
                err_msg = f'Captcha Network/Timeout exception occurred: {self._exc(err)}. ' \
                          f'Will try again in {SLEEP_PAUSE} secs.'
                _err(err_msg)
                time.sleep(SLEEP_PAUSE)
                continue

            if isinstance(result, str):
                msg = f'Received string response (probably server error). Will try again in {SLEEP_PAUSE} secs.'
                _log(msg)
                time.sleep(SLEEP_PAUSE)
                continue

            self._delete_tmp_image()
            captcha_id = result.get('captchaId')
            code = result.get('code')
            self.result['captcha_id'] = captcha_id
            self.result['code'] = code
            msg = f'Received captcha result for job {job_id}. Captcha id: {captcha_id}, code: {code}'
            _log(msg)
            return self.result

        self._delete_tmp_image()
        err_msg = f'Captcha time out: failed to get code from captcha API during {DEFAULT_TIMEOUT} secs.'
        _err(err_msg)
        self._error(err_msg)
        return self.result

    def report(self, _id, correct=True):
        try:
            return self.api.report(_id, correct)
        except (NetworkException, Exception):
            pass


if __name__ == '__main__':
    base_dir = os.path.dirname(__file__)
    # image = os.path.join(base_dir, 'captcha_tests/image.jpeg')
    image = os.path.join(base_dir, 'captcha_tmp/7612e9f4-88db-41e1-980d-a06853eb951f.jpg')
    solver = Solver()
    res = solver.solve(image, 1)
    print(res)
    print(type(res))
