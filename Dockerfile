FROM python:3.9.9-buster AS node

WORKDIR /opt/project

EXPOSE 8555

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH .
ENV TNB_IN_DOCKER true

# TODO(dmu) LOW: Optimize images size by deleting no longer needed files after installation
# We added build-essential to avoid hard to track issues later if add some package that requires it.
# Need to remove it later (when we stabilize list of dependencies) for the sake of image size optimization.
RUN set -xe \
    && apt-get update \
    && apt-get install build-essential \
    && pip install pip==21.3.1 virtualenvwrapper poetry==1.1.12

# For image build optimization purposes we install depdendencies here (so changes in the source code will not
# require dependencies reinstallation)
COPY ["pyproject.toml", "poetry.lock", "./"]
RUN poetry run pip install pip==21.3.1
RUN poetry install

COPY ["LICENSE", "README.rst", "./"]
COPY node node
RUN poetry install  # this installs the source code itself, since depenencies are installed before

COPY scripts/dockerized-node-run.sh ./run.sh
RUN chmod a+x run.sh

FROM nginx:1.20.2-alpine AS reverse-proxy

RUN rm /etc/nginx/conf.d/default.conf
COPY ./node/config/settings/templates/nginx.conf /etc/nginx/conf.d/node.conf
