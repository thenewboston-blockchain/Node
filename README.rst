=============
Project Setup
=============


Set up the project
++++++++++++++++++

Follow the steps below to set up the project on your environment.

1. Install poetry
2. Run `poetry install`
3. Create a `.env` file containing the following variables::

    DJANGO_SETTINGS_MODULE=config.settings.local
    MONGO_DB_NAME=blockchain
    MONGO_HOST=127.0.0.1
    NODE_SIGNING_KEY=a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f
    POSTGRES_DB_NAME=node
    POSTGRES_HOST=127.0.0.1
    POSTGRES_PASSWORD=thenewboston
    POSTGRES_USER=thenewboston
    SECRET_KEY=django-insecure-^m3d4yj1zic931$2t3z_b()(xz-_34c3sjeh_4v41rf#-2j8qs
