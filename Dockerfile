FROM python:3.9.9-buster AS node

WORKDIR /opt/project

EXPOSE 8555

RUN set -xe \
    && apt-get update \
    && pip install \
        pip==21.3.1 \
        poetry==1.1.12

COPY [ \
    "LICENSE", \
    "README.rst", \
    "INSTALL.linux.rst", \
    "INSTALL.macos.rst", \
    "Makefile", \
    "./" \
]
COPY node node

COPY ["pyproject.toml", "poetry.lock", "./"]
RUN make install

COPY scripts/entrypoint.sh .
RUN chmod a+x entrypoint.sh

ENTRYPOINT ./entrypoint.sh

FROM nginx:1.20.2-alpine AS reverse-proxy

RUN rm /etc/nginx/conf.d/default.conf
COPY ./node/config/settings/templates/nginx.conf /etc/nginx/conf.d/node.conf
