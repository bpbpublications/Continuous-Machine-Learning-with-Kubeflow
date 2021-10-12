FROM python:3.7-slim-stretch

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc mono-mcs g++ git curl && \
    rm -rf /var/lib/apt/lists/*



RUN mkdir /app
WORKDIR /app

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
RUN python get-pip.py
RUN rm get-pip.py
RUN pip install --upgrade pip
RUN apt-get update && yes | apt-get upgrade
RUN apt-get install -y libsm6 libxext6 libxrender-dev
RUN apt-get install -y protobuf-compiler python-pil python-lxml python-pip python-dev git
RUN apt-get update && apt-get install -y protobuf-compiler python-pil python-lxml
ADD requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

ADD preprocessing.py /app/preprocessing.py
RUN chmod +x /app/preprocessing.py



ENTRYPOINT ["python"]
CMD ["/app/preprocessing.py"]

