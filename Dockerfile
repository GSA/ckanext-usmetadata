ARG CKAN_VERSION=2.9
FROM openknowledge/ckan-dev:${CKAN_VERSION}
ARG CKAN_VERSION

RUN pip install --upgrade pip

COPY . /app

RUN pip install -r /app/requirements.txt -r /app/dev-requirements.txt -e /app
