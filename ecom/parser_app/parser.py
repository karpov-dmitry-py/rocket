import time
from typing import Dict, Any
from datetime import datetime
from datetime import timedelta

import pytz
import requests
import csv
import os.path
from random import choice
from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.wait import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.webdriver.common.by import By
# noinspection PyPackageRequirements
from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
from django.conf import settings as project_settings

from .proxy import ProxyManager
from .helpers import _log
from .helpers import _err


# TEST_URL2 = 'https://pokupki.market.yandex.ru/product/dushevaia-stoika-bravat-opal-f6125183cp-a-rus-khrom/' \
#             '13189953?show-uid=16070308423349822257006001&offerid=htYSTQ69Z9t2xYMvPwYopA'
#
# TEST_URL3 = 'https://pokupki.market.yandex.ru/product/gigienicheskii-dush-vstraivaemyi-lemark-plus-advance-' \
#             'lm1219c-khrom/1881772768?show-uid=16078875381409844855606004&offerid=ZWkBGAvM5Lnr7EcC06lmpg'
#
# TEST_URL4 = 'https://pokupki.market.yandex.ru/product/dushevoi-nabor-garnitur-vidima-orion-b4227aa-ba004aa-khrom/' \
#             '1632236?show-uid=16084771131237112433306006&offerid=sLc39hfqHXlRrapRlpcaOA'


class Parser:

    def __init__(self, job, region_code, _type='product'):

        self._proxies = ProxyManager(get_from_api=False).get_proxies()
        self._timeout = (3.05, 10)
        self._set_session()

        product = job.product
        self._job = job
        self._url = product.url
        self._region_code = region_code
        self._region = str(job.region)

        if _type not in self._supported_parsing_types():
            # TODO - update job with error=true and details
            raise ValueError(f'Parser error! Wrong parsing type ("{_type}") passed in for job with id: {self._job.id}')

        self.update_job()
        if _type == 'product':
            self.parse_product_page(url=self._url)
        elif _type == 'category':
            self.parse_category(url=self._url)

    def _set_session(self):
        self._session = requests.Session()

    @staticmethod
    def _supported_parsing_types():
        return (
            'product',
            'category',
        )

    def update_job(self, job=None, status=None, result_file=None):
        progress_status = 'progress'
        final_status = 'done'

        job = job or self._job
        status = status or progress_status
        job.status = status

        if result_file:
            job.result_file = result_file

        if status == final_status:
            timezone = pytz.timezone(zone=project_settings.TIME_ZONE)
            job.end_date = datetime.now(timezone)
            delta = job.end_date - job.start_date
            job.duration = round(delta.total_seconds(), 2)

        job.save()

    @staticmethod
    def _save_content(content, filename):
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'w') as f:
            f.write(content)

    def _prepare_url(self, url):
        result = f'{url}&lr={self._region_code}'
        return result

    @staticmethod
    def _create_webdriver(proxy, time_to_wait=10):
        options = Options()
        options.headless = True
        wire_options = {
            'proxy': proxy
        }
        driver = webdriver.Firefox(options=options, seleniumwire_options=wire_options)
        driver.implicitly_wait(time_to_wait)  # secs
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

    def parse_category(self, url):
        pass

    def parse_product_page(self, url=None, source=None):

        base_dir = os.path.dirname(__file__)
        result_dir = 'static/parser_app/product'
        filename = f'product_{self._job.id}.txt'
        full_path = os.path.join(base_dir, result_dir, filename)
        with open(full_path, 'w') as file:
            file.write(f'This is the result for product parsing: {self._job.id}')
        self.update_job(status='done', result_file=filename)
        return

        # if not (url or source):
        #     err_msg = f'No url or source provided for parsing: {url}'
        #     _err(err_msg)
        #     return
        #
        # if url and not source:
        #     url = self._prepare_url(url)
        #     source = self._get_source(url)
        #     if not source:
        #         err_msg = f'No content received for url: {url}'
        #         _err(err_msg)
        #         return
        #     self._save_content(source, 'run2_msk.html')
        # try:
        #     soup = BeautifulSoup(source, 'lxml')
        #     self._remove_bad_elements(soup)
        # except Exception as err:
        #     err_msg = f'Failed to build bs4 tree from source of url: {url}. ' \
        #               f'Error: {self._exc(err)}'
        #     _err(err_msg)
        #     return
        #
        # data = self._get_data_empty_dict()
        # try:
        #     # url, id
        #     if url:
        #         _id = url.split('?')[0].split('/')[-1]
        #         data['id'] = _id
        #         data['url'] = url
        #
        #     # title
        #     title = soup.find("h1", class_="b_rPzd7GVCYx b_1s00-3EuYB")
        #     if title:
        #         data['title'] = title.text
        #
        #     # categories
        #     categories = soup.find_all("span", class_="b_2_ymxwgqvC")
        #     category = '/'.join(self._values(categories)[1:])
        #     data['category'] = category
        #
        #     # stats
        #     stats = soup.find_all("span", class_="text b_3l-uEDOaBN b_1keKGH6ida b_3HJsMt3YC_ b_QDV8hKAp1G")
        #     stats = self._values(stats)
        #     data['purchase_count'] = self._puchase_count(stats)
        #     data['recommend_rate'] = self._recommend_rate(stats)
        #     data['view_count'] = self._view_count(stats)
        #
        #     # reviews
        #     reviews = soup.find("span", class_="b_2MBnkkD0XY")
        #     data['review_count'] = self._review_count(reviews.text)
        #
        #     # storage
        #     storage = soup.find("div", {'data-zone-name': 'warehouse'})
        #     if storage:
        #         data['storage'] = storage.text
        #
        #     # seller
        #     seller = soup.find("a", {'data-tid': 'f54fb4c8 3d02273a'})
        #     if seller:
        #         data['seller'] = seller.text
        #
        #     # brand
        #     brand = soup.find("div", class_="b_12Md0AuR7n")
        #     if brand:
        #         data['brand'] = self._brand(brand.text)
        #
        #     # delivery dates
        #     deliveries = soup.find_all("div", class_="b_37t9OXssoz")
        #     deliveries = self._values(deliveries)
        #     if deliveries:
        #         data['pickup_days'] = self._days(self._delivery_date(deliveries, 'самовывоз'))
        #         data['delivery_days'] = self._days(self._delivery_date(deliveries, 'курьер'))
        #
        #     # images
        #     main_image = soup.find("div", class_="b_2ke8Y2fll7")
        #     if main_image:
        #         data['image_url'] = self._image_url(main_image)
        #
        #     thumbnails = soup.find_all("li", class_="b_3ldhZi3q64")
        #     data['image_count'] = len(thumbnails)
        #
        #     # prices
        #     prices = []
        #     old_price = soup.find("span", {'data-auto': 'old-price'})
        #     if old_price:
        #         data['old_price'] = self._price(old_price.text)
        #
        #     main_price = soup.find("div", class_="b_2r89I1B_sZ")
        #     if main_price:
        #         main_price = self._price(main_price.text)
        #         data['main_price'] = main_price
        #         prices.append(main_price)
        #         if not old_price:
        #             data['old_price'] = main_price
        #
        #     discount = soup.find("div", class_="b_1KTAcrzTNV")
        #     if discount:
        #         data['discount_rate'] = self._numeric(discount.text)
        #
        #     competitor_prices = soup.find_all("span",
        #                                       class_="b_1pTV0mQZJz b_37FeBjfnZk b_HBgx6P83Bo _brandTheme_default")
        #     if competitor_prices:
        #         for item in competitor_prices:
        #             price = self._price(item.text)
        #             if price:
        #                 prices.append(price)
        #
        #     min_price = min(prices)
        #     if min_price:
        #         data['min_price'] = min_price
        #     data['seller_count'] = len(prices)
        #
        #     # rating, eval, recommendation
        #     star_rating = soup.find("span", class_="b_3C0DxleA0I")
        #     if star_rating:
        #         data['star_rating'] = star_rating.text
        #
        #     eval_count = soup.find("span", class_="b_2Wc288IN4J")
        #     if eval_count:
        #         data['eval_count'] = self._eval_count(eval_count.text)
        #
        #     if data['recommend_rate'] is None:
        #         recommend_rate = soup.find("span", class_="b_128RDniUsM")
        #         if recommend_rate:
        #             data['recommend_rate'] = recommend_rate.text
        #
        #     self.save_to_scv(data=data)

        # except Exception as err:
        #     err_msg = f'Failed to parse product page: {data.get("id")}. Error: {self._exc(err)}'
        #     _err(err_msg)

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

    @staticmethod
    def _now():
        _format = '%d-%m-%Y %H:%M:%S'
        return datetime.now().strftime(_format)

    def save_to_scv(self, data: Dict[str, Any]) -> None:
        data['parse_date'] = self._now()
        data['region'] = self._region

        _id = data.get('id') or 'no_id'
        filename = f'product_{_id}.csv'
        file_path = os.path.join(os.path.dirname(__file__), filename)
        try:
            with open(file_path, 'w', encoding='utf8', newline='') as csv_file:
                fieldnames = [key for key in data.keys()]
                writer = csv.DictWriter(f=csv_file, delimiter=',', fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow(data)
            _log(f'Successfully saved file: {filename}')
        except Exception as err:
            err_msg = f'Failed to save file: {filename}. Error: {self._exc(err)}'
            _err(err_msg)
            raise Exception(err_msg)

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

    def _get_source(self, url):
        if not self._proxies:
            err_msg = 'No available proxies found!'
            _err(err_msg)
            return

        proxies_count = len(self._proxies)
        max_attempts = proxies_count
        attempts = 0
        last_used_proxy = None

        while attempts <= max_attempts:
            # pick random proxy but not the last one used
            if proxies_count > 1:
                while True:
                    proxy = choice(self._proxies)
                    if proxy != last_used_proxy:
                        last_used_proxy = proxy
                        break
            else:
                proxy = self._proxies[0]
            driver = self._create_webdriver(proxy=proxy)
            try:
                driver.get(url)

                elem = driver.find_element_by_tag_name('html')
                scroll_count = 11
                for i in range(1, scroll_count):
                    elem.send_keys(Keys.PAGE_DOWN)
                    if i < scroll_count - 1:
                        time.sleep(0.5)

                source = driver.page_source
                if self._is_captcha(source):
                    _log(f'Received captcha for url: {url}. Will try again')
                    self._sleep(3)
                    attempts += 1
                    continue

                _log(f'Received content for url: {url}')
                return source

            except Exception as err:
                err_msg = f'Error getting url: {url}. Error: {self._exc(err)}'
                _err(err_msg)
                self._sleep(10)
                return
            finally:
                driver.close()
                driver.quit()

        err_msg = f'Tried all {proxies_count} proxies and FAILED to get content of product page: {url}.'
        _err(err_msg)

    def get(self, url):
        url = self._prepare_url(url)
        for proxy in self._proxies:
            self._session.proxies = proxy
            response = self._session.get(url, timeout=self._timeout)

            # error
            if response.status_code != 200:
                err_msg = f'Error received when requesting url: {url}. \n' \
                          f'Proxy used: {proxy}.\n' \
                          f'Response status: {response.status_code}. ' \
                          f'Response text: {response.text}'
                _err(err_msg)
                continue

            # success
            file_name = 'response.html'
            with open(file_name, 'w') as f:
                f.write(response.text)
            _log(f'Successfully saved response to file: {file_name}')
            return

        err_msg = f'No content received with all my proxies tried out! Check my proxies!'
        _err(err_msg)

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
# parser = Parser()
# parser.parse_product_page(url=TEST_URL2)
# parser.parse_product_page(url=TEST_URL3)
# source = parser.read_file('3_sellers.html')
# source = parser.read_file('run1.html')
# source = parser.read_file('run2_msk.html')
# source = parser.read_file('response1.html')
# parser.parse_product_page(source=source)

# parser.parse_product_page(url=TEST_URL4)


if __name__ == '__main__':
    main()
