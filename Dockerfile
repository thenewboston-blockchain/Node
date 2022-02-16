FROM python:3.9.9-buster AS node

ARG NODE_LIST_SOURCE=http://34.221.75.138:8555/

WORKDIR /opt/project

EXPOSE 8555

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV TNB_IN_DOCKER true
# TODO(dmu) LOW: Is there a way to read WORKDIR value instead of hardcoding `/opt/project`?
ENV TNB_NODE_LIST_JSON_PATH /opt/project/node-list.json

# TODO(dmu) LOW: Optimize images size by deleting no longer needed files after installation
# We added build-essential to avoid hard to track issues later if add some package that requires it.
# Need to remove it later (when we stabilize list of dependencies) for the sake of image size optimization.
RUN set -xe \
    && apt-get update \
    && apt-get install build-essential \
    && pip install pip==22.0.2 virtualenvwrapper poetry==1.1.12

# For image build optimization purposes we install depdendencies here (so changes in the source code will not
# require dependencies reinstallation)
COPY ["pyproject.toml", "poetry.lock", "./"]
RUN poetry run pip install pip==22.0.2
RUN poetry install

COPY ["LICENSE", "README.rst", "./"]
COPY node node
RUN poetry install  # this installs just the source code itself, since dependencies are installed before

COPY scripts/dockerized-node-run.sh ./run.sh
RUN chmod a+x run.sh

RUN TNB_SECRET_KEY=dummy TNB_NODE_SIGNING_KEY=dummy poetry run python -m node.manage list_nodes $NODE_LIST_SOURCE > $TNB_NODE_LIST_JSON_PATH || echo '[]' > $TNB_NODE_LIST_JSON_PATH

FROM nginx:1.20.2-alpine AS node-reverse-proxy

RUN rm /etc/nginx/conf.d/default.conf
COPY ./node/config/settings/templates/nginx.conf /etc/nginx/conf.d/node.conf

FROM mongo:5.0.5-focal AS node-mongo
# Make MongoDB a replica set to support transactions. Based on https://stackoverflow.com/a/68621185/1952977
RUN apt-get update && apt-get install patch
RUN echo '12f900454e89facfb4c297f83c57b065  /usr/local/bin/docker-entrypoint.sh' > /tmp/docker-entrypoint.sh.md5 && \
    md5sum -c /tmp/docker-entrypoint.sh.md5 || \
    echo 'Looks like /usr/local/bin/docker-entrypoint.sh has been modified since scripts/docker-entrypoint.sh.patch was create. Please, validate and recalculate the checksum'

# How to create scripts/docker-entrypoint.sh.patch
# 1. Download the original file:
#    wget https://github.com/docker-library/mongo/raw/master/5.0/docker-entrypoint.sh
#    ( wget https://github.com/docker-library/mongo/raw/b5c0cd58cb5626fee4d963ce05ba4d9026deb265/5.0/docker-entrypoint.sh )
# 2. Make a copy of it:
#    cp docker-entrypoint.sh docker-entrypoint-patched.sh
# 3. Add required modifications to docker-entrypoint-patched.sh
# 4. Create patch:
#    diff -u docker-entrypoint.sh docker-entrypoint-patched.sh > scripts/docker-entrypoint.sh.patch
# 5. Clean up:
#    rm docker-entrypoint.sh docker-entrypoint-patched.sh
COPY scripts/docker-entrypoint.sh.patch .
RUN patch /usr/local/bin/docker-entrypoint.sh docker-entrypoint.sh.patch
RUN mkdir -p /etc/mongo-key && chown mongodb:mongodb /etc/mongo-key

CMD ["--replSet", "rs", "--keyFile", "/etc/mongo-key/mongodb.key"]
