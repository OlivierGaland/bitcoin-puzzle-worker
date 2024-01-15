FROM nvidia/cuda:12.1.0-base-ubuntu20.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python python3-pip 

# https://devopscube.com/run-docker-in-docker/    #TODO a simpler way to access docker exe inside container ?
RUN apt-get update && \
    apt-get -qy full-upgrade && \
    apt-get install -qy curl && \
    apt-get install -qy curl && \
    curl -sSL https://get.docker.com/ | sh

WORKDIR /www
COPY ./www .

WORKDIR /app
RUN mkdir ssl
COPY ./src .

ENTRYPOINT ["python3", "watchdog.py"]
