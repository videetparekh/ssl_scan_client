FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y curl python3.9 python3.9-dev python3.9-distutils

# Default python3-pip installs python3.8 and links pip to it.
WORKDIR /tmp
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.9 get-pip.py

WORKDIR /app
ADD ssl_scan_client .
RUN pip3 install .

WORKDIR /workspace
