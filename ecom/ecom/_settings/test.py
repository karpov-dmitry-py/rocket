import json


def test():
    data = {
        'secret_key': 'em75j0dje2y&t_(qjmv-w51%mc(xyykrt^)rwj&6^k0vlftd#+',
        'dev': {
        },
        'prod': {
            'debug': False,
            'allowed_hosts': ['marketplace-master.ru', 'www.marketplace-master.ru'],
            'dbs': {
                'default': {
                    'ENGINE': 'django.db.backends.mysql',
                    'NAME': 'u1273130_default',
                    'USER': 'u1273130_default',
                    'PASSWORD': '_mC7onrM',
                    'HOST': 'localhost',
                }
            }
        }
    }
    with open('_settings.json', 'w') as file:
        json.dump(data, file, indent=4)


if __name__ == '__main__':
    test()
