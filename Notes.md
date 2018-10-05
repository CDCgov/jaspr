---
title: Developer Notes

Creating HTML Version of this file
---
----------------------------------

To create the HTML version of these notes install pandoc from https://pandoc.org and then use the batch file _createhtmldocs.bat_ to generate an HTML file

Next Steps
-----------

1. [x] Set up a basic template for the main page
1. [x] Add bootstrap and break out basic page layout
1. [x] Add basic color scheme so it isn't ugly
1. [x] Add file upload function (flask-uploads)
1. [x] Remove CDN from graphing
1. [x] Load data into Pandas
1. [x] Set up a graph page using Bokeh
1. [x] Put data table into tab (temporary)
1. [x] Connect data grid to graph
1. [x] fix Juypter to restart from old or recreate
1. [ ] Add custom x axis labels for titers
1. [ ] Flesh out settings form
1. [ ] Add configuration (yaml)
1. [ ] Flesh out calls to bas service tier
1. [ ] Add pdf file creation functionality
1. [ ] Add validation so that only xslx files can be uploaded
1. [ ] Plan for use of ReactJS components



Creating and Running the jaspr project container for development
-----------------------------------------------------------------

__Using provided Python tooling__

This project is designed to be developed using a Docker container as a running environment.  The python file to create this container is _jasprbuild.py_.  Here are the instructions to use this tool:

	jasprbuild.py

	This will build and run the jaspr software within
	a docker container

	-b(--build) to build the container
	-r(--run) to run the container

if you want to run things manually, here are the commands that will get you stgarted:

__To create container__

docker-compose build

__to run container__

docker run -i -t -v c:/Projects/jaspr/app:/app -p 5000:5000 -e FLASK_APP=hello.py -w /app --rm cdcflu/jaspr:v1



Other Notes/random stuff
------------------------

1.) Download miniconda docker package and run bash shell
	a.) docker pull conda/miniconda3
	b.) docker run -i -t conda/miniconda3 /bin/bash --allow-root bokeh

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

docker run -i -t  -v c:/frunk:/frunk -p 8888:8888 continuumio/anaconda3 /bin/bash -c "/opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip='*'  --no-browser --allow-root

I get the error:
docker: Error response from daemon: driver failed programming external connectivity on endpoint flamboyant_kepler (caadd7788899e6a680608e91274e185cd29a077a0c85f016a209ad2c125669e0): Error starting userland proxy: mkdir /port/tcp:0.0.0.0:8888:tcp:172.17.0.2:8888: input/output error.
[SOLVED]It seems that the problem goes away when I restart docker.  

[PROBLEM]  cannot run Jupyter by using container name as host
[SOLVED] You need to specify localhost:8888
