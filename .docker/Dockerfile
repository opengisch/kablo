# pull official base image
FROM python:3.12-bookworm as base



RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libproj-dev \
    gdal-bin \
    gettext \
    shared-mime-info \
    tzdata \
    graphviz \
    graphviz-dev \
    && ln -fs /usr/share/zoneinfo/Europe/Zurich /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata

COPY . /kablo
WORKDIR /kablo
ENV PYTHONUNBUFFERED 1


FROM base as production

ENV ENV=PROD
RUN pip install -r requirements.txt


FROM base as dev

ENV ENV=DEV
ENV PYTHONDONTWRITEBYTECODE 1
RUN pip install -r requirements_dev.txt
