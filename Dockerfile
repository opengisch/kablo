# pull official base image
FROM python:3.12-bookworm

# set work directory
WORKDIR /code


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    libproj-dev \
    gdal-bin \
    gettext \
    shared-mime-info \
    tzdata \
    && ln -fs /usr/share/zoneinfo/Europe/Zurich /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata

# install dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy files in another location to solved windows rights issues
# These files are only used during build process and by entrypoint.sh for dev

ARG ENV
WORKDIR /code
COPY requirements_dev.txt requirements_dev.txt
COPY requirements.txt requirements.txt

RUN if [ "$ENV" = "DEV" ] ; \
    then \
    echo "Installing development dependencies..." \
    && pip3 install -r requirements_dev.txt \
    && echo "########################################" \
    && echo "# Installed development dependencies   #" \
    && echo "########################################"; \
    else \
    pip3 install -r requirements.txt \
    && echo "########################################" \
    && echo "# Installed production dependencies    #" \
    && echo "########################################"; \
    fi

COPY . /code/
