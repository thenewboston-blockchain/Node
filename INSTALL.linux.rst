Local development environment setup
===================================

This section describes how to setup development environment for Debian-based distributions
(tested on Linux Mint 20.2 specifically)
REMOVE THIS CHANGE

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

    #. Install Python 3.9.9::

        pyenv install 3.9.9
        pyenv local 3.9.9 # run from the root of this repo (`.python-version` file should appear)

#. Install Poetry::

    export PIP_REQUIRED_VERSION=21.3.1
    pip install pip==${PIP_REQUIRED_VERSION} && \
    pip install virtualenvwrapper && \
    pip install poetry==1.1.12 && \
    poetry config virtualenvs.path ${HOME}/.virtualenvs && \
    poetry run pip install pip==${PIP_REQUIRED_VERSION}

#. Setup local configuration for running code on host::

    mkdir -p local && \
    cp node/config/settings/templates/settings.dev.py ./local/settings.dev.py && \
    cp node/config/settings/templates/settings.unittests.py ./local/settings.unittests.py

    # Edit files if needed
    vim ./local/settings.dev.py
    vim ./local/settings.unittests.py

#. Configure settings for running dockerized node::

    make dot-env

#. Install dependencies, run migrations, etc by doing `Update`_ section steps

#. Create superuser::

    make superuser

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

#. (in a separate terminal) Run node::

    # TODO(dmu) HIGH: We need to be able initialize blockchain with known signing keys for testing
    #                 https://thenewboston.atlassian.net/browse/BC-153
    make genesis
    make run-server

#. [Optional] (in a separate terminal) Run another Node for testing and debugging communications between nodes::

    cp node/config/settings/templates/settings.dev.py ./local/settings.dev.node2.py
    # Add `DATABASES['default']['NAME'] = 'node2'` to ./local/settings.dev.node2.py
    export TNB_LOCAL_SETTINGS_PATH=./local/settings.dev.node2.py
    make migrate
    make superuser
    # TODO(dmu) LOW: Parametrize `make run-server` with port number and use it instead
    poetry run python -m node.manage runserver 127.0.0.1:8556

#. [Optional] (in a separate terminal) Run Node for local development purposes with Docker

    make up-dev

Development tools
+++++++++++++++++

#. Make migrations::

    make migrations

Run production Node
===================

Common configuration
++++++++++++++++++++

#. Install Docker on target machine according to https://docs.docker.com/engine/install/
   (known working: Docker version 20.10.7, build f0df350)
#. Add your user to docker group::

    sudo usermod -aG docker $USER
    exit

#. Install Docker Compose  on target machine according to https://docs.docker.com/compose/install/
   (known working: docker-compose version 1.29.2, build 5becea4c)


Configure continuous deployment
+++++++++++++++++++++++++++++++

#. Create deploy ssh key on target machine::

    # Use empty pass phrase
    ssh-keygen -f ~/.ssh/github
    cat ~/.ssh/github.pub >> ~/.ssh/authorized_keys

#. Create github repository secrets::

    NODE_CONTINUOUS_DEPLOYMENT_ENABLED=True
    NODE_DEPLOY_SSH_KEY=<content of ~/.ssh/github>
    NODE_DEPLOY_SSH_HOST=<IP-address or domain name of target machine>
    NODE_DEPLOY_SSH_USER=<username that has the corresponding public in ~/authorized_keys>
