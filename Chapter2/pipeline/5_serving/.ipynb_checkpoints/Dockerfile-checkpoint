FROM python:3.7-slim-stretch

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc mono-mcs g++ git curl bash && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . .
ADD servebreast.py /app/servebreast.py




CMD ["python","servebreast.py"]


