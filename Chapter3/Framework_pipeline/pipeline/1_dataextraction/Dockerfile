FROM python:3.7-slim-stretch

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc mono-mcs g++ git curl && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
RUN mkdir ~/.kaggle
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt


ADD dataextract.py /app/dataextract.py
ADD kaggle.json /app/kaggle.json

RUN chmod +x /app/dataextract.py
RUN cp /app/kaggle.json  ~/.kaggle
RUN  chmod 600 ~/.kaggle/kaggle.json

ENTRYPOINT ["python"]
CMD ["/app/dataextract.py"]
