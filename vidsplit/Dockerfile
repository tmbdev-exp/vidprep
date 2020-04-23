FROM ubuntu:20.04 AS gobuild
ENV LC_ALL=C
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -qqy golang-1.14
ENV PATH=/usr/lib/go-1.14/bin:$PATH
RUN apt-get install -qqy git
RUN apt-get install -qqy libczmq-dev libsodium-dev
ENV GOPATH=/root/go
RUN mkdir /root/go
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

RUN apt-get install -qqy libswscale-dev libtbb2 libtbb-dev libjpeg-dev libpng-dev \
        libtiff-dev libavformat-dev libpq-dev python3-pip
RUN apt-get install -qqy libav*-dev
RUN apt-get install -qqy ffmpeg

#RUN apt-get install -qqy python3-opencv
RUN pip3 install numpy matplotlib scipy scikit-image scikit-learn imageio h5py
RUN pip3 install jupyter jupyterlab rise bash_kernel
RUN pip3 install torch torchvision
RUN pip3 install typer
RUN pip3 install av

COPY --from=gobuild /root/go/bin/tarp /usr/local/bin/tarp
RUN apt-get install -qqy libczmq-dev libsodium-dev

#RUN pip3 install git+git://github.com/tmbdev/tarproc
RUN pip3 install git+git://github.com/tmbdev/webdataset
RUN apt-get install -qqy memstat
COPY ./extract-segments /usr/local/bin
