import math
from bs4 import BeautifulSoup

def test():
    with open('category parsing job 1 content.html') as file:
        source = file.read()
    soup = BeautifulSoup(source, 'lxml')
    listing_stats = soup.find("div", class_="b_2StYqKhlBr b_1wAXjGKtqe")
    if not listing_stats:
        raise ValueError('No listing stats div parsed from a category first page')
    listing_str = listing_stats.text
    if not listing_str:
        raise ValueError('Empty listing stats parsed from a category first page')
    stats = []
    for word in listing_str.split():
        if word.isdigit():
            stats.append(word)
    if len(stats) < 2:
        raise ValueError(f'Parsed {len(stats)} stats values from a category first page.')
    products_per_page, products_total = stats[0], stats[1]
    pages_count = math.ceil(products_total/products_per_page)


    products = soup.find_all("a", class_="b_3ioN70chUh b_Usp3kX1MNT b_3Uc73lzxcf")
    pass




if __name__ == '__main__':
    test()


