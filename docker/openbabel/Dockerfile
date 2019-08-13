FROM ubuntu:18.04

RUN apt-get update -y
RUN apt-get install -y \
  python3-pip \
  python3-dev \
  pkg-config \
  libopenbabel-dev \
  swig

COPY requirements.txt /app/
RUN pip3 install -r /app/requirements.txt

COPY src/* /app/

WORKDIR /app

ENTRYPOINT ["python3", "main.py"]
