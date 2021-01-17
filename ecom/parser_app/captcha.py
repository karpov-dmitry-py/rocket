import time
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

    def solve(self, image_path, job_id):
        self.result = {
            'image_path': image_path,
            'job_id': job_id,
            'captcha_id': None,
            'code': None,
            'error': None
        }
        if not os.path.isfile(image_path):
            err_msg = f'Image file not found for job {job_id}: {image_path}'
            _err(err_msg)
            self._error(err_msg)
            return self.result

        start_time = time.time()
        while not self._is_timeout(start_time):
            try:
                result = solver.api.normal(image_path, caseSensitive=1)
            except (SolverExceptions, ValidationException, ApiException, Exception) as err:
                err_msg = f'API related exception occurred: {self._error(err)}'
                _err(err_msg)
                self._error(err_msg)
                return self.result
            except (NetworkException, TimeoutException) as err:
                err_msg = f'API related exception occurred: {self._error(err)}. Will try again in {SLEEP_PAUSE} secs.'
                _err(err_msg)
                time.sleep(SLEEP_PAUSE)
                continue

            if isinstance(result, str):
                err_msg = f'Received string response (probably server error). Will try again in {SLEEP_PAUSE} secs.'
                _err(err_msg)
                time.sleep(SLEEP_PAUSE)
                continue

            # TODO - delete image for this job
            captcha_id = result.get('captchaId')
            code = result.get('code')
            self.result['captcha_id'] = captcha_id
            self.result['code'] = code
            msg = f'Received captcha result for job {job_id}. Captcha id: {captcha_id}, code: {code}'
            _log(msg)
            return self.result

        # TODO - delete image for this job
        err_msg = f'Time out occurred: failed to get code from captcha API during {DEFAULT_TIMEOUT} secs.'
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
    image = os.path.join(base_dir, 'captcha_tests/image.jpeg')
    solver = Solver()
    res = solver.solve(image, 1)
    print(res)
    print(type(res))
