from .base import *

DEBUG = True

# Postgres
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

# Mongo
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')
MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_PORT = 27017
