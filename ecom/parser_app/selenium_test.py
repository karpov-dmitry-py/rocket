from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

TEST_URL1 = 'https://pokupki.market.yandex.ru/product/dushevaia-stoika-lemark-tropic-lm7002c-khrom/' \
            '1729156733?show-uid=16069023726419173634506002&offerid=j1whkfwvdtmdnD_4fMO3wg'

TEST_URL2 = 'https://pokupki.market.yandex.ru/product/ruchnoi-dush-grohe-new-tempesta-ii-2760110e-khrom/' \
            '1885512059?show-uid=16072690384132468612606014&offerid=TCGniUoGinZrhQFFNMvYMw'

# PROXY = 'http://KNUQxcoIRE:1vQ2CqpcJe@91.243.60.106:25186'
PROXY = 'http://ZntfJLb1dk:cH7mVCs46F@185.103.253.100:19870'

options = Options()
options.headless = True
url = f'{TEST_URL1}&lr=213'
wire_options = {
    'proxy': {
        'http': PROXY,
        'https': PROXY
    }
}

driver = webdriver.Firefox(options=options, seleniumwire_options=wire_options)
driver.implicitly_wait(15)  # seconds
driver.get(TEST_URL1)
with open('selenium_res4.html', 'w') as f:
    f.write(driver.page_source)
driver.quit()
