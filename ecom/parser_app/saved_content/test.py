from bs4 import BeautifulSoup

def test():
    with open('category parsing job 1 content.html') as file:
        source = file.read()
    soup = BeautifulSoup(source, 'lxml')
    products_stats = soup.find("div", class_="b_2StYqKhlBr b_1wAXjGKtqe")
    products = soup.find_all("a", class_="b_3ioN70chUh b_Usp3kX1MNT b_3Uc73lzxcf")
    pass




if __name__ == '__main__':
    test()


