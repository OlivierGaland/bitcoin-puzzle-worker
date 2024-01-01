FROM nvidia/cuda:12.1.0-devel-ubuntu20.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get install git nano curl -y vim dos2unix
RUN apt-get install -y python3 python3-pip 

WORKDIR /app
RUN git clone https://github.com/brichard19/BitCrack

WORKDIR /app/benchmark
COPY ./src .
RUN dos2unix ./info.py ./benchmark.py

ENTRYPOINT ["python3", "tools/initialize.py"]
