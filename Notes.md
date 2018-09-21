---
title: Developer Notes
---

Creating HTML Version of this file
----------------------------------

To create the HTML version of these notes install pandoc from https://pandoc.org and then use the batch file _createhtmldocs.bat_ to generate an HTML file

Creating and Running the Jasper project container for development
-----------------------------------------------------------------

__Using provided Python tooling__

This project is designed to be developed using a Docker container as a running environment.  The python file to create this container is _jasperbuild.py_.  Here are the instructions to use this tool:

	jasperbuild.py

	This will build and run the Jasper software within	
	a docker container

	-b(--build) to build the container
	-r(--run) to run the container

if you want to run things manually, here are the commands that will get you stgarted:

__To create container__

docker-compose build

__to run container__

docker run -i -t -v c:/Projects/jasper/app:/app -p 5000:5000 -e FLASK_APP=hello.py -w /app --rm cdcflu/jasper:v1

Other Notes/random stuff
------------------------

1.) Download miniconda docker package and run bash shell
	a.) docker pull conda/miniconda3
	b.) docker run -i -t conda/miniconda3 /bin/bash --allow-rootbokeh

2.) Install Flask, Bokeh, plugin framework (James will tell me the name), YAML
or JASN config
	a.) Upgrade pip
		pip install --upgrade pip
	b.) Install FLASK
		pip install FLASK
	c.) Install bokeh
		conda install bokeh (NOTE: Need to find a way to avoid
interactive Y/N Question)


[PROBLEM]
If this doesn't work to run Jupyter:

docker run -i -t -p 8888:8888 continuumio/anaconda3 /bin/bash -c "/opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip='*' --port=8888 --no-browser --allow-root"

I get the error:
docker: Error response from daemon: driver failed programming external connectivity on endpoint flamboyant_kepler (caadd7788899e6a680608e91274e185cd29a077a0c85f016a209ad2c125669e0): Error starting userland proxy: mkdir /port/tcp:0.0.0.0:8888:tcp:172.17.0.2:8888: input/output error.
[SOLVED]It seems that the problem goes away when I restart docker.  

[PROBLEM]  cannot run Jupyter by using container name as host
[SOLVED] You need to specify localhost:8888



