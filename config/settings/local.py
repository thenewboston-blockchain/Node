from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': os.getenv('POSTGRES_HOST'),
        'NAME': os.getenv('POSTGRES_DB_NAME'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'PORT': 5432,
        'USER': os.getenv('POSTGRES_USER'),
    }
}
