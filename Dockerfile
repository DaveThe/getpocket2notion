FROM python:3.7-alpine3.8

# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update
RUN apk add chromium chromium-chromedriver

# set display port to avoid crash
ENV DISPLAY=:99

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

ENV APP_HOME /app
WORKDIR $APP_HOME
COPY app .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD [ "python", "./main.py" ]