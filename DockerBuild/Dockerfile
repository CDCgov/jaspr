#gather miniconda
FROM continuumio/miniconda3

MAINTAINER Garrett Peterson "garrettp@yaharasoftware.com"

# Copy the current directory contents into the container at /build
ADD . /build

# Set the working directory to /build
WORKDIR /build

# Update pip
RUN pip install --upgrade pip

# Add libraries we need have
RUN pip install --trusted-host pypi.python.org -r requirements.txt

WORKDIR /app

EXPOSE 5000/tcp

VOLUME /app

CMD /bin/bash -i -c "pip install -e . ; flask run -h 0.0.0.0"
