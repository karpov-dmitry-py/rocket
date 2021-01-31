# _*_ coding: utf-8 _*_
import codecs
import math
import time
import uuid
from builtins import Exception
from typing import Dict, Any
from datetime import datetime
from datetime import timedelta
from urllib.parse import urljoin

import requests
import csv
import os
import os.path
from random import choice
from selenium.webdriver.common.keys import Keys

# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By

# noinspection PyPackageRequirements
from seleniumwire import webdriver

# from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
# from django.utils.encoding import force_str

from .proxy import ProxyManager
from .captcha import Solver as CaptchaSolver
from .helpers import _log
from .helpers import _err
from .helpers import _now
from .helpers import _now_as_str


class Parser:

    def __init__(self, job, region_code, _type='category'):

        self._job = job
        if not region_code:
            err_msg = f'Found no region code in db for {_type} parsing job: {job.id}'
            _err(err_msg)
            self.update_job(status='done', error=err_msg)
            return

        if _type not in self._supported_parsing_types():
            err_msg = f'Wrong parsing type ("{_type}") passed in for job: {job.id}'
            _err(err_msg)
            self.update_job(status='done', error=err_msg)
            return

        try:
            self._proxies = ProxyManager(get_from_api=True).get_proxies()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, Exception) as err:
            err_msg = f'Failed to get proxies from Proxy class. Error: {self._exc(err)}'
            _err(err_msg)
            self.update_job(status='done', error=err_msg)
            return

        msg = f'Retrieved {len(self._proxies)} active proxies from Proxy class.'
        _log(msg)
        if not self._proxies:
            err_msg = msg
            _err(err_msg)
            self.update_job(status='done', error=err_msg)
            return

        self._timeout = (3.05, 10)
        self._set_session()

        _object = job.product if _type == 'product' else job.category
        self._url = _object.url
        self._region_code = region_code
        self._region = str(job.region)
        self._solver = CaptchaSolver()
        self._stats = {
            'current': 0,
            'total': 0,
            'captcha': {
                'submitted': 0,
                'good': 0,
                'bad': 0
            }
        }
        self._type = _type
        self._result_file_path = None
        self._result_file_name = None

        self.update_job()
        if _type == 'product':
            try:
                self.parse_product(url=self._url)
                self.update_job(status='done')
            except (AttributeError, Exception) as err:
                err_msg = f'Parse product error: {self._exc(err)}'
                _err(err_msg)
                self.update_job(status='done', error=err_msg)
                return

        elif _type == 'category':
            try:
                self.parse_category(url=self._url)
            except (AttributeError, Exception) as err:
                err_msg = f'Parse category error: {self._exc(err)}'
                _err(err_msg)
                self.update_job(status='done', error=err_msg)

    def _set_session(self):
        self._session = requests.Session()

    def _current_state(self):
        current = self._stats.get('current')
        total = self._stats.get('total')

        if not (current and total):
            return ''

        percent = round(current / total, 2) * 100
        _cap = self._stats['captcha']
        result = f'Done {current} of {total} products: {percent}%. Captcha: submitted: {_cap["submitted"]}, ' \
                 f'good: {_cap["good"]}, bad: {_cap["bad"]}'

        return result

    def _parse_captcha_image(self, html_source, job_id=None):
        job_id = job_id or self._job.id
        result = {
            'job_id': job_id,
            'image_path': None,
            'error': None
        }
        target = 'https://pokupki.market.yandex.ru/captchaimg'
        msg = f'Trying to parse captcha image url from source for job {job_id}.'
        _log(msg)
        try:
            _end = html_source.split(target)[1].split('"')[0]
            url = f'{target}{_end}'
            msg = f'Successfully parsed captcha image url from source for job {job_id}. URL: {url}'
            _log(msg)
            download_image_result = self._download_content(url=url)
            if error := download_image_result.get('error'):
                result['error'] = error
                return result

            result['image_path'] = download_image_result.get('save_path')
            return result

        except (IndexError, AttributeError, Exception) as err:
            err_msg = f'Failed to parse image_url from source for job {job_id}. Error: {self._exc(err)}'
            _err(err_msg)
            result['error'] = err_msg
            return result

    def _solve_captcha(self, source, job_id=None):
        job_id = job_id or self._job.id
        result = {
            'code': None,
            'error': None
        }
        get_image_path_result = self._parse_captcha_image(source)
        if error := get_image_path_result.get('error'):
            result['error'] = error
            return result

        image_path = get_image_path_result.get('image_path')
        self._stats['captcha']['submitted'] += 1
        solve_result = self._solver.solve(image_path, job_id)
        if error := solve_result.get('error'):
            result['error'] = error
            return result

        return solve_result

    @staticmethod
    def _supported_parsing_types():
        return (
            'product',
            'category',
        )

    def update_job(self, job=None, status=None, result_file=None, error=None):
        progress_status = 'progress'
        final_status = 'done'
        need_stats_statuses = (progress_status, final_status)

        job = job or self._job
        status = status or progress_status
        job.status = status

        if result_file:
            job.result_file = result_file

        if error:
            job.error = error

        if status in need_stats_statuses:
            now = _now()
            delta = now - job.start_date
            total_seconds = round(delta.total_seconds())
            duration_as_str = str(timedelta(seconds=total_seconds))
            job.duration = duration_as_str
            if status == 'done':
                job.end_date = now
            if state := self._current_state():
                job.comment = state

        job.save()

    @staticmethod
    def _save_content(content, filename):
        base_dir = os.path.dirname(__file__)
        _log(f'Base dir: {base_dir}')
        save_dir = 'saved_content'
        path = os.path.join(base_dir, save_dir, filename)
        with open(path, 'w') as f:
            f.write(content)
        _log(f'Saved content to file: {path}')

    def _prepare_url(self, url, page_number=None):
        # TODO - implement individual logic for each marketplace; only Yandex Pokupki is implemented so far
        result = f'{url}&lr={self._region_code}'
        if page_number:
            result = f'{result}&page={page_number}'
        return result

    @staticmethod
    def _create_webdriver(proxy):
        options = Options()
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        wire_options = {
            'proxy': proxy
        }
        driver = webdriver.Firefox(
            # driver = webdriver.Chrome(
            # executable_path='/usr/local/bin/geckodriver',
            # executable_path='/usr/bin/chromedriver',

            firefox_binary='/usr/bin/firefox',
            firefox_options=options,
            # chrome_options=options,
            seleniumwire_options=wire_options,
            service_log_path='/tmp/geckodriver.log',
            # service_log_path='/tmp/chromedriver.log',
        )
        return driver

    @staticmethod
    def _exc(_exception):
        return f'{_exception.__class__.__name__}: {str(_exception)}'

    @staticmethod
    def read_file(filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path) as source:
            content = source.read()
        return content

    @staticmethod
    def _get_data_empty_dict():
        data = {
            'id': None,
            'category': None,
            'title': None,
            'url': None,
            'min_price': None,
            'main_price': None,
            'old_price': None,
            'discount_rate': 0,
            'currency': 'RUB',
            'storage': None,
            'seller_count': None,
            'star_rating': None,
            'eval_count': None,
            'review_count': None,
            'recommend_rate': None,
            'purchase_count': None,
            'view_count': None,
            'brand': None,
            'pickup_days': None,
            'delivery_days': None,
            'seller': None,
            'image_url': None,
            'image_count': None,
            'video_url': None,
            'parse_date': None,
            'region': None,
        }
        return data

    @staticmethod
    def _remove_bad_elements(soup):
        class_ = 'b_KgZT-UYxg1'
        targets = (
            'с этим товаром смотрят',
            'с этим товаром покупают',
        )
        for div in soup.find_all("div", class_=class_):
            if any(target in str(div).lower() for target in targets):
                div.decompose()

    def _soup(self, source, url=None):
        try:
            soup = BeautifulSoup(source, 'lxml')
            return {'soup': soup}
        except Exception as err:
            err_msg = f'Failed to build bs4 tree from source of url: {url}. ' \
                      f'Error: {self._exc(err)}'
            return {'error': err_msg}

    def parse_category(self, url, source=None):
        job_id = self._job.id

        # get first page
        if not source:
            url = self._prepare_url(url)
            get_source_result = self._get_source(url, _type='category', time_to_wait=0,
                                                 scroll_page=False)
            if error := get_source_result.get('error'):
                err_msg = f'Failed to get category first page source for job {job_id}. Error: {error}'
                self.update_job(status='done', error=err_msg)
                return
            source = get_source_result.get('source')
            # filename = f'category_parsing_job_{job_id}_content.html'
            # self._save_content(source, filename)

        soup_result = self._soup(source, url)
        if error := soup_result.get('error'):
            _err(error)
            self.update_job(status='done', error=error)
            return
        soup = soup_result.get('soup')

        # parsing
        listing_stats = soup.find("div", class_="b_2StYqKhlBr b_1wAXjGKtqe")
        if not listing_stats:
            err_msg = 'Failed to parse product pagination info from category first page'
            _err(err_msg)
            self.update_job(status='done', error=error)
            return

        listing_str = listing_stats.text
        stats = []
        for word in listing_str.split():
            if word.isdigit():
                stats.append(word)
        if len(stats) < 2:
            raise ValueError(f'Parsed not enough {len(stats)} products count stats from category first page: {stats}')
        products_per_page, products_total = int(stats[0]), int(stats[1])
        self._stats['total'] = products_total
        products_processed = 0
        pages_count = math.ceil(products_total / products_per_page)
        base_url = self._job.category.marketplace.url

        # walking the pages
        for page_number in range(1, pages_count + 1):
            # get content starting with second page
            if page_number > 1:
                current_url = self._prepare_url(url=url, page_number=page_number)
                get_source_result = self._get_source(current_url, _type='category', time_to_wait=0,
                                                     scroll_page=False)
                if error := get_source_result.get('error'):
                    err_msg = f'Failed to get source for category page #{page_number} for job {job_id}. Error: {error}'
                    self.update_job(status='done', error=err_msg)
                    return
                source = get_source_result.get('source')
                soup_result = self._soup(source, url)
                if error := soup_result.get('error'):
                    err_msg = f'Failed to build bs4 tree for category page #{page_number} for job {job_id}. ' \
                              f'Error: {error}'
                    _err(err_msg)
                    self.update_job(status='done', error=err_msg)
                    return
                soup = soup_result.get('soup')

            # products
            products = soup.find_all("a", class_="b_3ioN70chUh b_Usp3kX1MNT b_3Uc73lzxcf")
            for product in products:
                products_processed += 1
                _log(f'Processing product # {products_processed} of {products_total}')

                href = product.attrs.get('href')
                product_url = urljoin(base_url, href)
                product_url = self._prepare_url(url=product_url)

                product_parse_result = self.parse_product(url=product_url)
                self._stats['current'] = products_processed

                if error := product_parse_result.get('error'):
                    err_msg = f'Parsing product error for url: {product_url}.' \
                              f'Error: {error}'
                    _err(err_msg)
                    self.update_job(status='done', error=err_msg)
                    return

        self.update_job(status='done')

    @staticmethod
    def _attr(_object, attr='text'):
        return hasattr(_object, attr)

    def parse_product(self, url=None, source=None):
        if not (url or source):
            err_msg = f'No url or source provided for parsing: {url}'
            _err(err_msg)
            self.update_job(status='done', error=err_msg)
            return {'error': err_msg}

        if url and not source:
            url = self._prepare_url(url)
            get_source_result = self._get_source(url)
            if error := get_source_result.get('error'):
                err_msg = f'Error occurred when getting source for url: {url}.' \
                          f'Error: {error}'
                _err(err_msg)
                self.update_job(status='done', error=err_msg)
                return {'error': err_msg}

            source = get_source_result.get('source')
            if not source:
                err_msg = f'No content (empty content) received for url: {url}'
                _err(err_msg)
                self.update_job(status='done', error=err_msg)
                return {'error': err_msg}

        soup_result = self._soup(source, url)
        if error := soup_result.get('error'):
            _err(error)
            self.update_job(status='done', error=error)
            return {'error': error}
        soup = soup_result.get('soup')
        self._remove_bad_elements(soup)
        data = self._get_data_empty_dict()
        try:
            # url, id
            if url:
                _id = url.split('?')[0].split('/')[-1]
                data['id'] = _id
                data['url'] = url

            # title
            title = soup.find("h1", class_="b_rPzd7GVCYx")
            if title:
                data['title'] = title.text

            # categories
            categories = soup.find_all("span", class_="b_2_ymxwgqvC")
            if categories:
                category = '/'.join(self._values(categories)[1:])
                data['category'] = category

            # stats
            stats = soup.find_all("span", class_="text")
            if stats:
                stats = self._values(stats)
                data['purchase_count'] = self._puchase_count(stats)
                data['recommend_rate'] = self._recommend_rate(stats)
                data['view_count'] = self._view_count(stats)

            # reviews
            reviews = soup.find("span", class_="b_2MBnkkD0XY")
            if reviews:
                data['review_count'] = self._review_count(reviews.text)

            # storage
            storage = soup.find("div", {'data-zone-name': 'warehouse'})
            if storage:
                data['storage'] = storage.text

            # seller
            seller = soup.find("a", {'data-tid': 'f54fb4c8 3d02273a'})
            if seller:
                data['seller'] = seller.text

            # brand
            brand = soup.find("div", class_="b_12Md0AuR7n")
            if brand:
                data['brand'] = self._brand(brand.text)

            # delivery dates
            deliveries = soup.find_all("div", class_="b_37t9OXssoz")
            if deliveries:
                deliveries = self._values(deliveries)
                if deliveries:
                    data['pickup_days'] = self._days(self._delivery_date(deliveries, 'самовывоз'))
                    data['delivery_days'] = self._days(self._delivery_date(deliveries, 'курьер'))

            # images
            main_image = soup.find("div", class_="b_2ke8Y2fll7")
            if main_image:
                data['image_url'] = self._image_url(main_image)

            images = soup.find_all("li", class_="b_3ldhZi3q64")
            images_count = 0
            if images:
                images_count = len(images)

            # more_images_label
            more_images_label = soup.find("span", class_="b_3OmJUywakO")
            if more_images_label:
                try:
                    more_images_count = int(''.join(char for char in more_images_label.text if char.isdigit()))
                    images_count += more_images_count
                except (IndexError, Exception) as err:
                    err_msg = f'Failed to parse exact number from "more images" label. Error: {self._exc(err)}'
                    _err(err_msg)
                    self.update_job(status='done', error=err_msg)
                    return {'error': err_msg}
            data['image_count'] = images_count or 1

            # prices
            prices = []
            old_price = soup.find("span", {'data-auto': 'old-price'})
            if old_price:
                data['old_price'] = self._price(old_price.text)

            main_price = soup.find("div", class_="b_2r89I1B_sZ")
            if main_price:
                main_price = self._price(main_price.text)
                data['main_price'] = main_price
                prices.append(main_price)
                if not old_price:
                    data['old_price'] = main_price
                if old_price != main_price:
                    discount = soup.find("div", class_="b_1KTAcrzTNV")
                    if discount:
                        data['discount_rate'] = self._numeric(discount.text)

            # competitor_offers
            seller_count = 1  # main seller
            competitor_offers = soup.find_all("div", {'data-zone-name': 'alternativeOffer'})
            if competitor_offers:
                seller_count += len(competitor_offers)
                for offer in competitor_offers:
                    try:
                        _str = offer.text.split('\xa0')[1]
                        price = ''.join(char for char in _str if char.isdigit())
                        prices.append(int(price))
                    except (IndexError, Exception) as err:
                        err_msg = f'Failed to parse a competitor price. Error: {self._exc(err)}'
                        _err(err_msg)
                        self.update_job(status='done', error=err_msg)
                        return {'error': err_msg}
            data['seller_count'] = seller_count

            # min_price
            min_price = min(prices)
            if min_price:
                data['min_price'] = min_price

            # rating, eval, recommendation
            star_rating = soup.find("span", class_="b_3C0DxleA0I")
            if star_rating:
                data['star_rating'] = star_rating.text

            eval_count = soup.find("span", class_="b_2Wc288IN4J")
            if eval_count:
                data['eval_count'] = self._eval_count(eval_count.text)

            if data['recommend_rate'] is None:
                recommend_rate = soup.find("span", class_="b_128RDniUsM")
                if recommend_rate:
                    data['recommend_rate'] = recommend_rate.text

            self.save_to_scv(data=data)
            return {'ok': True}

        except (KeyError, AttributeError, Exception) as err:
            err_msg = f'Failed to parse product page: {data.get("id")}. Error: {self._exc(err)}'
            _err(err_msg)
            self.update_job(status='done', error=err_msg)
            return {'error': err_msg}

    @staticmethod
    def _values(results):
        return [item.text for item in results]

    def _image_url(self, main_image_element):
        try:
            url = main_image_element.next.attrs['src']
            url = url.split('//')[1]
            return url
        except (AttributeError, KeyError, IndexError) as err:
            err_msg = f'Failed to parse image url. Error: {self._exc(err)}'
            _err(err_msg)
            return

    def _days(self, _date):
        if not _date:
            return

        days = [str(day) for day in range(1, 32)]
        months = {
            'января': 1,
            'февраля': 2,
            'марта': 3,
            'апреля': 4,
            'мая': 5,
            'июня': 6,
            'июля': 7,
            'августа': 8,
            'сентября': 9,
            'октября': 10,
            'ноября': 11,
            'декабря': 12,
        }

        words = _date.lower().split()
        cleared_words = []
        for word in words:
            if word in days or word in list(months.keys()):
                cleared_words.append(word)

        if not cleared_words:
            _err(f'Failed to find day and month in delivery date string: {_date}')
            return

        if len(cleared_words) > 2:
            cleared_words = cleared_words[1:]

        try:
            day, month = int(cleared_words[0]), cleared_words[1]
            month = months[month]
        except (IndexError, Exception) as err:
            err_msg = f'Failed to parse date from date string: {_date}. Error: {self._exc(err)}'
            _err(err_msg)
            return

        now = datetime.now()
        current_day = now.day
        current_month = now.month

        if month == current_month:
            return day - current_day

        days_to_date = 0
        next_date = now
        while True:
            days_to_date += 1
            next_date = next_date + timedelta(days=1)
            if current_month != next_date.month and next_date.day == day:
                return days_to_date

    @staticmethod
    def _delivery_date(items, target):
        for text in items:
            if target in text.lower():
                return text

    def _price(self, string):
        target = '\xa0'  # nbsp
        try:
            result = int(string.strip().split(target)[0].replace(' ', ''))
            return result
        except (IndexError, TypeError, ValueError) as err:
            err_msg = f'Failed to parse numeric value from string: {string}. ' \
                      f'Error: {self._exc(err)}'
            _err(err_msg)

    @staticmethod
    def _numeric(string):
        try:
            return int(string)
        except (TypeError, ValueError, Exception):
            return 0

    @staticmethod
    def _puchase_count(stats):
        target = 'покуп'
        for string in stats:
            if target in string.lower():
                try:
                    result = string.strip().split()[0]
                    if result.isdigit():
                        return int(result)
                except IndexError:
                    pass
        return 0

    @staticmethod
    def _recommend_rate(stats):
        target = 'рекоменд'
        for string in stats:
            if target in string.lower():
                try:
                    result = string.strip().split()[0]
                    if '%' in result:
                        return result
                except IndexError:
                    pass

    @staticmethod
    def _view_count(stats):
        target = 'интересовал'
        for string in stats:
            if target in string.lower():
                try:
                    result = string.strip().split()[0]
                    if result.isdigit():
                        return int(result)
                except IndexError:
                    pass
        return 0

    @staticmethod
    def _review_count(string):
        target = 'отзыв'
        if target in string.lower():
            try:
                result = string.strip().split()[0]
                if result.isdigit():
                    return int(result)
            except IndexError:
                pass
        return 0

    @staticmethod
    def _eval_count(string):
        try:
            result = string.strip().split()[0]
            if result.isdigit():
                return int(result)
        except IndexError:
            pass
        return 0

    @staticmethod
    def _brand(brand):
        target = 'Все товары бренда '
        if target in brand:
            try:
                result = brand.split(target)[1].strip()
                return result
            except (IndexError, AttributeError):
                pass

    def save_to_scv(self, data: Dict[str, Any]) -> None:
        data['parse_date'] = _now_as_str()
        data['region'] = self._region
        job_id = self._job.id
        if not self._result_file_path:
            base_dir = os.path.dirname(__file__)
            result_dir = f'static/parser_app/{self._type}'
            _id = str(uuid.uuid4())
            filename = f'{self._type}_parsing_job_{job_id}_{_id}.csv'
            full_path = os.path.join(base_dir, result_dir, filename)
            self._result_file_path = full_path
            self._result_file_name = filename
        try:
            with open(self._result_file_path, 'a', encoding='utf8', newline='') as csv_file:
                fieldnames = [key for key in data.keys()]
                writer = csv.DictWriter(f=csv_file, delimiter=',', fieldnames=fieldnames, dialect=csv.excel)

                # file does not exist yet
                if not os.stat(self._result_file_path).st_size:
                    writer.writeheader()
                    writer.writerow(data)
                    _log(f'Successfully created file for job {job_id}: {self._result_file_path}')
                    self.update_job(result_file=self._result_file_name)
                    return

                # file exists
                writer.writerow(data)
                _log(f'Successfully updated file for job {job_id}: {self._result_file_path}')
                self.update_job()

        except Exception as err:
            err_msg = f'Failed to create/update file: {self._result_file_path}. Error: {self._exc(err)}'
            _err(err_msg)
            self.update_job(status='done', error=err_msg)

    @staticmethod
    def _is_captcha(source):
        if not source:
            return False
        source = source.lower()
        indicators = (
            'запросы, поступившие с вашего ip-адреса, похожи на автоматические',
            'yandex.ru/support/captcha',
        )
        return any(item in source for item in indicators)

    @staticmethod
    def _sleep(time_to_sleep):
        _log(f'Sleeping for {time_to_sleep} secs...')
        for i in range(1, time_to_sleep + 1):
            _log(f'..............{i}')
            time.sleep(1)

    @staticmethod
    def _helping_actions(driver, url, time_to_wait=0, scroll_page=True):
        if time_to_wait:
            driver.implicitly_wait(time_to_wait)  # secs
        driver.get(url)

        # scroll page
        if scroll_page:
            elem = driver.find_element_by_tag_name('html')
            scroll_count = 11
            for i in range(1, scroll_count):
                elem.send_keys(Keys.PAGE_DOWN)
                if i < scroll_count - 1:
                    time.sleep(2)

    def _get_captcha_input_elements(self, driver):
        filename = 'live_captcha.html'
        with open(filename, 'w') as file:
            file.write(self._source(driver))
            _log(f'Saved captcha source to: {filename}')

        result = {
            'input': None,
            'submit': None,
            'error': None
        }

        _input = 'input-wrapper__content'
        _submit = 'submit'

        try:
            result['input'] = driver.find_element_by_class_name(_input)
            result['submit'] = driver.find_element_by_class_name(_submit)
        except (AttributeError, Exception) as err:
            err_msg = f'Failed to parse captcha input elements from source with webdriver. Error: {self._exc(err)}'
            _err(err_msg)
            result['error'] = err_msg

        return result

    def _source(self, driver):
        try:
            source = driver.page_source
            # _bytes = source.encode()
            # _log(f'Encoded original source to bytes.')
            #
            # filename = 'saved_source.html'
            # _log(f'Writing str source content to: {filename}')
            # with codecs.open(filename, 'wb') as file:
            #     file.write(_bytes)
            # _log(f'Wrote _bytes to: {filename}')

        except (UnicodeEncodeError, UnicodeDecodeError, Exception) as err:
            err_msg = f'Failed to retrieve driver.page_source. Error: {self._exc(err)}'
            _err(err_msg)
            raise Exception(err_msg)

        _log(f'Source type: {type(source)}')
        return source

    def _get_source(self, url, _type='product', time_to_wait=10, scroll_page=True):
        proxies_count = len(self._proxies)
        attempts = 0
        last_used_proxy = None
        while attempts <= proxies_count:
            attempts += 1
            msg = f'Attempt {attempts}. Getting source of {_type} page: {url}'
            _log(msg)

            # pick random proxy but not the last one used
            if proxies_count > 1:
                while True:
                    proxy = choice(self._proxies)
                    if proxy != last_used_proxy:
                        # noinspection PyUnusedLocal
                        last_used_proxy = proxy
                        break
            else:
                proxy = self._proxies[0]

            driver = self._create_webdriver(proxy=proxy)
            try:
                self._helping_actions(driver, url, time_to_wait, scroll_page)
                source = self._source(driver)
                if not self._is_captcha(source):
                    _log(f'Received source for url: {url}')
                    return {'source': source}

                # got captcha
                _log(f'Received captcha for url: {url}. Will try to solve it.')
                captcha_attempts = 0
                captcha_max_attempts = 10
                captcha_submit_pause = 10  # secs

                while captcha_attempts <= captcha_max_attempts:
                    captcha_attempts += 1
                    msg = f'Attempt {attempts}. Solving captcha of {_type} page: {url}'
                    _log(msg)

                    elements = self._get_captcha_input_elements(driver)
                    if error := elements.get('error'):
                        return {'error': f'captcha get input elements from source error: {error}'}

                    solve_result = self._solve_captcha(source)
                    if error := solve_result.get('error'):
                        return {'error': f'captcha solve error: {error}'}

                    # submit captcha
                    code = solve_result.get('code')
                    elements['input'].send_keys(code)
                    elements['submit'].click()
                    msg = f'Submitted captcha form and now sleeping for {captcha_submit_pause} secs.'
                    _log(msg)
                    time.sleep(captcha_submit_pause)

                    self._helping_actions(driver, url, time_to_wait, scroll_page)
                    source = self._source(driver)

                    solved_captcha_id = solve_result.get('captcha_id')
                    if not self._is_captcha(source):
                        # captcha solved successfully
                        self._stats['captcha']['good'] += 1
                        self._solver.report(solved_captcha_id)
                        _log(f'Received source for url: {url}')
                        return {'source': source}

                    # continue to another captcha attempt

                    err_msg = f'Incorrect captcha case: {solve_result}'
                    _err(err_msg)
                    self._stats['captcha']['bad'] += 1
                    self._solver.report(solved_captcha_id, False)
                    continue

                else:
                    err_msg = f'Failed to solve captcha after {captcha_attempts} attempts for job {self._job.id}.' \
                              f' URL: {url}'
                    _err(err_msg)
                    return {'error': f'Captcha max attempts {captcha_max_attempts} error: {err_msg}'}

            except Exception as err:
                err_msg = f'Error getting content for url: {url}. Error: {self._exc(err)}'
                _err(err_msg)
                self.update_job(status='done', error=err_msg)
                return {'error': err_msg}
            finally:
                driver.close()
                driver.quit()

        err_msg = f'Tried all {proxies_count} proxies and FAILED to get content of {_type} page: {url}.'
        _err(err_msg)
        return {'error': err_msg}

    def _download_content(self, url, goal='captcha image url', ext='jpg'):
        for proxy in self._proxies:
            self._session.proxies = proxy
            response = self._session.get(url, timeout=self._timeout)

            # error handling
            if response.status_code != 200:
                err_msg = f' Non-200 response received when downloading {goal}: {url}. \n' \
                          f'Proxy used: {proxy}.\n' \
                          f'Response status: {response.status_code}. ' \
                          f'Response text: {response.text}'
                _err(err_msg)
                continue

            # save content
            raw = response.content
            filename = f'{str(uuid.uuid4())}.{ext}'
            base_dir = os.path.dirname(__file__)
            save_dir = 'captcha_tmp'
            save_path = os.path.join(base_dir, save_dir, filename)
            with open(save_path, 'wb') as f:
                f.write(raw)
            _log(f'Successfully saved response to file: {save_path}')
            return {'save_path': save_path}

        err_msg = f'No content received for {goal} with all {len(self._proxies)} proxies tried out! Check proxies!' \
                  f'URL: {url}'
        _err(err_msg)
        return {'error': err_msg}

    # not used
    def post(self, url, data, headers, cookies):
        self._session.headers.update(headers)
        response = self._session.post(url=url, data=data, cookies=cookies)
        result = response.text
        file_name = 'post_response1.json'
        with open(file_name, 'w') as f:
            f.write(result)
        _log(f'Response status: {response.status_code}. Successfully saved response text to file: {file_name}')


def main():
    pass
    # parser = Parser(region='Екатеринбург')
    # parser = Parser(1, 2)
    # parser.parse_product_page(url=TEST_URL2)
    # parser.parse_product_page(url=TEST_URL3)
    # source = parser.read_file('product_parsing_job_9_.html')
    # source = parser.read_file('run1.html')
    # source = parser.read_file('run2_msk.html')
    # source = parser.read_file('response1.html')
    # parser.parse_product_page(source=source)
    # parser.parse_product_page(url=TEST_URL4)

    # parser = Parser(1, 2)
    # source = parser.read_file('product_parsing_job_13_.html')
    # parser.parse_product_page(source=source)


if __name__ == '__main__':
    main()
