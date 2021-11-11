Local development environment setup
===================================

This section describes how to setup development environment for Debian-based distributions
(tested on Linux Mint 18.3 specifically)

Initial setup
+++++++++++++
Once initial setup is done only corresponding `Update`_ section should be performed
to get the latest version for development.

#. Install prerequisites::

    apt update
    apt install git

#. Install prerequisites (
   as prescribed at https://github.com/pyenv/pyenv/wiki/Common-build-problems )::

    # TODO(dmu) MEDIUM: Remove dependencies that are not really needed
    apt update && \
    apt install make build-essential libssl-dev zlib1g-dev libbz2-dev \
                libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
                libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev \
                python-openssl libpq-dev

#. Install Docker according to https://docs.docker.com/engine/install/
   (known working: Docker version 20.10.1, build 831ebea)
#. Add your user to docker group::

    sudo usermod -aG docker $USER
    exit

#. Install Docker Compose according to https://docs.docker.com/compose/install/
   (known working: docker-compose version 1.27.4, build 40524192)

#. Clone the repository::

    git clone git@github.com:thenewboston-developers/Node.git

#. [if you have not configured it globally] Configure git::

    git config user.name 'Firstname Lastname'
    git config user.email 'youremail@youremail_domain.com'

#. Ensure you have Python 3.9.x installed and it will be used for running the project (you can
   do it with optional steps below)
#. [Optional] Install Python 3.9.x with ``pyenv``

    #. Install and configure `pyenv` according to
       https://github.com/pyenv/pyenv#basic-github-checkout

    #. Install Python 3.9.6::

        # TODO(dmu) MEDIUM: Migrate to Python 3.10.x
        #                   https://thenewboston.atlassian.net/browse/BC-133
        pyenv install 3.9.6
        pyenv local 3.9.6  # run from the root of this repo (`.python-version` file should appear)

#. Install Poetry::

    export PIP_REQUIRED_VERSION=21.3.1
    pip install pip==${PIP_REQUIRED_VERSION} && \
    pip install virtualenvwrapper && \
    pip install poetry==1.1.11 && \
    poetry config virtualenvs.path ${HOME}/.virtualenvs && \
    poetry run pip install pip==${PIP_REQUIRED_VERSION}

#. Create a `.env` file containing the following variables::

    cat <<EOF > .env
    DJANGO_SETTINGS_MODULE=node.config.settings.local
    MONGO_DB_NAME=blockchain
    MONGO_HOST=127.0.0.1
    NODE_SIGNING_KEY=a37e2836805975f334108b55523634c995bd2a4db610062f404510617e83126f
    SECRET_KEY=django-insecure-^m3d4yj1zic931$2t3z_b()(xz-_34c3sjeh_4v41rf-2j8qs
    EOF

#. Install dependencies, run migrations, etc by doing `Update`_ section steps

Update
++++++
#. (in a separate terminal) Run dependency services::

    make up-dependencies-only

#. Update::

    make update

Run quality assurance tools
+++++++++++++++++++++++++++

#. Lint::

    make lint

#. Test::

    make test

#. Lint then test::

    make lint-and-test

Run
+++

#. (in a separate terminal) Run only dependency services with Docker::

    make up-dependencies-only

#. (in a separate terminal) Run Node::

    make run-server
