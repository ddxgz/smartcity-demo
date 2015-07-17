FROM ubuntu:14.04

# backup old sources.list
RUN mv /etc/apt/sources.list /etc/apt/sources.list.bk

ADD sources.list /etc/apt/sources.list

RUN apt-get -qqy update && apt-get install -y \
    curl \
    python \
    python-dev \
    python-pip \
    gunicorn 


# for copy requirements.txt to container
#COPY . /restapi

WORKDIR /restapi

RUN pip install -r requirements.txt
