FROM python:3.7-slim-stretch

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc mono-mcs g++ git curl && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir /app
WORKDIR /app

ADD requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt



ADD vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5 /app/vgg16_weights_tf_dim_ordering_tf_kernels_notop.h5
ADD train.py /app/train.py
ADD storage.py /app/storage.py
RUN chmod +x /app/train.py

ENTRYPOINT ["python"]
CMD ["/app/train.py"]
