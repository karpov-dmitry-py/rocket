import math
import os
from bs4 import BeautifulSoup


def _remove_bad_elements(soup):
    class_ = 'b_KgZT-UYxg1'
    targets = (
        'с этим товаром смотрят',
        'с этим товаром покупают',
    )
    for div in soup.find_all("div", class_=class_):
        if any(target in str(div).lower() for target in targets):
            div.decompose()

def test():
    with open('product_parsing_job_11_.html') as file:
        source = file.read()
    soup = BeautifulSoup(source, 'lxml')
    _remove_bad_elements(soup)
    old_price = soup.find("span", {'data-auto': 'old-price'})
    main_price = soup.find("div", class_="b_2r89I1B_sZ")
    discount = soup.find("div", class_="b_1KTAcrzTNV")
    competitor_prices1 = soup.find_all("span",
                                      class_="b_HBgx6P83Bo")
    competitor_price2 = soup.find_all("div", class_="b_3bZBOZx4nL")
    offers = soup.find_all("div", {'data-zone-name': 'alternativeOffer'})



    pass


if __name__ == '__main__':
    test()
