#gather miniconda
FROM continuumio/miniconda3

MAINTAINER Garrett Peterson "garrettp@yaharasoftware.com"

run apt-get update
run apt-get -y dist-upgrade
run apt-get -yq install net-tools nginx python-pip

# Copy the current directory contents into the container at /build
ADD . /build

# Set the working directory to /build
WORKDIR /build

# Update pip
RUN pip install --upgrade pip

# Add libraries we need have
RUN pip install --trusted-host pypi.python.org -r requirements.txt

RUN conda install -c conda-forge phantomjs
RUN conda install -c conda-forge selenium

WORKDIR /app

EXPOSE 5000/tcp

VOLUME /app

CMD /bin/bash -i -c "pip install -e . ; flask run -h 0.0.0.0"
