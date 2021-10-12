FROM python:3.7-slim-stretch

ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get -y install gcc mono-mcs g++ git curl bash && \
    rm -rf /var/lib/apt/lists/*

ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

ADD lightgbm_wandb.py /app/lightgbm_wandb.py
ADD lgb_classifier.txt /app/lgb_classifier.txt



# COPY . /app
WORKDIR /app

CMD ["python","lightgbm_wandb.py"]


