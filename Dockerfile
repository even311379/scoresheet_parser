# FROM python:3.6-slim
# WORKDIR /job
# COPY . /job
# RUN apt-get update
# EXPOSE 80
# ENV NAME World
# CMD ["jupyter","notebook"]

FROM ubuntu:latest


RUN apt-get update && apt-get install -y python3 \
    python3-pip
RUN apt-get install ocrmypdf -y
RUN apt-get install tesseract-ocr-chi-tra
RUN apt-get install build-essential libpoppler-cpp-dev pkg-config -y

COPY requirements.txt /tmp
WORKDIR /tmp

RUN pip3 install -r requirements.txt

# fix ascii issue
RUN apt-get install -y locales locales-all
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

# Create a new system user
RUN useradd -ms /bin/bash jupyter

# Change to this new user
USER jupyter

WORKDIR /home/jupyter
COPY . /home/jupyter




# Start the jupyter notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8080"]