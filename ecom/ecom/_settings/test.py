import json


def test():
    data = {
        'secret_key': 'em75j0dje2y&t_(qjmv-w51%mc(xyykrt^)rwj&6^k0vlftd#+',
        'dev': {},
        'prod': {
            'debug': True,
            'dbs': {
                'default': {
                    'NAME': 'rocket_db',
                    'ENGINE': 'mysql.connector.django',
                    'USER': 'rocket_user',
                    'PASSWORD': 'rocket_pswd',
                    'HOST': '127.0.0.1',
                    'PORT': '3306',
                    'OPTIONS': {
                        'autocommit': True,
                    },
                }
            }
        }
    }
    with open('_settings.json', 'w') as file:
        json.dump(data, file, indent=4)

if __name__ == '__main__':
    test()
