FROM ubuntu:20.04 AS gobuild
ENV LC_ALL=C
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -qqy golang-1.14
ENV PATH=/usr/lib/go-1.14/bin:$PATH
RUN apt-get install -qqy git
RUN apt-get install -qqy libczmq-dev libsodium-dev
RUN mkdir /root/go
ENV GOPATH=/root/go
WORKDIR /root
RUN go get -v github.com/tmbdev/tarp/tarp

FROM ubuntu:20.04

ENV LC_ALL=C
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update
RUN apt-get install -qqy build-essential cmake git wget unzip yasm pkg-config

RUN apt-get install -qqy curl

RUN apt-get install -qqy python-dev python-setuptools

RUN curl https://dl.google.com/dl/cloudsdk/release/google-cloud-sdk.tar.gz > /tmp/google-cloud-sdk.tar.gz
RUN mkdir -p /usr/local/gcloud && tar -C /usr/local/gcloud -xvf /tmp/google-cloud-sdk.tar.gz
RUN /usr/local/gcloud/google-cloud-sdk/install.sh
ENV PATH $PATH:/usr/local/gcloud/google-cloud-sdk/bin

RUN apt-get install -qqy python3 python3-pip
RUN pip3 install jupyter jupyterlab rise bash_kernel

RUN apt-get install -qqy libczmq-dev libsodium-dev
COPY --from=gobuild /root/go/bin /usr/local/bin
