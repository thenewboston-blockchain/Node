Local development environment setup
===================================

This section describes how to setup development environment for Debian-based distributions
(tested on Linux Mint 20.2 specifically)

Initial setup
+++++++++++++
Once initial setup is done only corresponding `Update`_ section should be performed
to get the latest version for development.

#. Install prerequisites (
   as prescribed at https://github.com/pyenv/pyenv/wiki/Common-build-problems and some other)::

    # TODO(dmu) MEDIUM: Remove dependencies that are not really needed
    # TODO(dmu) MEDIUM: These dependencies seem to be candidates for removal: tk-dev wget curl llvm
    sudo apt update && \
    apt install git make build-essential libssl-dev zlib1g-dev libbz2-dev \
                libreadline-dev libsqlite3-dev libncurses5-dev \
                libncursesw5-dev xz-utils libffi-dev liblzma-dev \
                python-openssl

#. Install Docker according to https://docs.docker.com/engine/install/
   (known working: Docker version 20.10.1, build 831ebea)

#. Add your user to docker group::

    sudo usermod -aG docker $USER
    exit  # you may actually need to reboot for group membership to take effect

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

    #. Install Python 3.9.8::

        pyenv install 3.9.8
        pyenv local 3.9.8 # run from the root of this repo (`.python-version` file should appear)

#. Install Poetry::

    export PIP_REQUIRED_VERSION=21.3.1
    pip install pip==${PIP_REQUIRED_VERSION} && \
    pip install virtualenvwrapper && \
    pip install poetry==1.1.11 && \
    poetry config virtualenvs.path ${HOME}/.virtualenvs && \
    poetry run pip install pip==${PIP_REQUIRED_VERSION}

#. Setup local configuration for running code on host::

    mkdir -p local && \
    cp node/config/settings/templates/settings.dev.py ./local/settings.dev.py && \
    cp node/config/settings/templates/settings.unittests.py ./local/settings.unittests.py

    # Edit files if needed
    vim ./local/settings.dev.py
    vim ./local/settings.unittests.py

#. [Optional] If you prefer override settings with environment variables defined in `.env` file::

    cp node/config/settings/templates/dotenv.dev .env

    # Edit file if needed
    vim .env

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
