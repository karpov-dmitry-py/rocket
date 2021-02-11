import os.path
# import json
# from helpers import _log

def testme():
    base_path = os.path.dirname(__file__)
    full_path = os.path.join(base_path, '01.html')
    try:
        with open(full_path, encoding='utf8', errors='ignore') as file:
            source = file.read()
    except (UnicodeDecodeError, Exception) as err:
        # _log(f'Exception occured: {str(err)}')
        with open(full_path, encoding='utf-8', errors='replace') as file:
            source = file.read()
    for i, char in enumerate(source, start=1):
        # print(f'{i}. {char}')
        _char = char

if __name__ == '__main__':
    testme()
