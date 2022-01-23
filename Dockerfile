# FROM python:3.8
FROM ubuntu:20.04
RUN apt-get update && apt-get -y update
RUN apt-get install -y build-essential python3.8 python3-pip
RUN pip3 -q install pip --upgrade

RUN mkdir src
WORKDIR src/
COPY . .

RUN pip3 install -r ./requirements.txt

CMD ["python3", "./parse_vacancies.py"]
