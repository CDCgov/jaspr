---
title: Developer Notes

Creating HTML Version of this file
---

* * *

To create the HTML version of these notes install pandoc from <https://pandoc.org> and then use the batch file _createhtmldocs.bat_ to generate an HTML file

* * *

export FLASK_APP=jaspr
If you are outside of the project directory make sure to provide the exact path to your application directory. Similiarly you can turn on “debug mode” with this environment variable:

export FLASK_DEBUG=true
In order to install and run the application you need to issue the following commands:

pip install -e .
flask run

* * *

## Next Steps

1.  [ ] Load example file into model and plot in linear space
1.  [ ] Add ability to plot log graph again
1.  [ ] Add custom x axis labels for titers
1.  [ ] Add custom x axis labels for titers
2.  [ ] Add labels (cp50, cp90 etc.)
3.  [ ] Flesh out settings form
4.  [ ] Add configuration loading (yaml)
5.  [ ] Add report file creation functionality
6.  [ ] Add validation so that only xslx files can be uploaded
8.  [x] Set up a basic template for the main page
9.  [x] Add bootstrap and break out basic page layout
10. [x] Add basic color scheme so it isn't ugly
11. [x] Add file upload function (flask-uploads)
12. [x] Remove CDN from graphing
13. [x] Load data into Pandas
14. [x] Set up a graph page using Bokeh
15. [x] Put data table into tab (temporary)
16. [x] Connect data grid to graph
17. [x] fix Juypter to restart from old or recreate
18. [x] create stubbed out API and wire up to prototype
19. [x] Wire in old help content
20. [x] Establish classes for data and load them in for use
21. [x] Wire in multi sample list
22. [x] Wire up individual charts and data
23. [x] Flesh out calls to base service tier
24. [x] Wire in grabbing data for each sample separately
25. [ ] Hook up the excel file reading functionality from legacy application

## Creating and Running the jaspr project container for development

**Using provided Python tooling**

This project is designed to be developed using a Docker container as a running environment.  The python file to create this container is _jasprbuild.py_.  Here are the instructions to use this tool:

    jasprbuild.py

    This will build and run the jaspr software within
    a docker container

    -b(--build) to build the container
    -r(--run) to run the container

if you want to run things manually, here are the commands that will get you stgarted:

**To create container**

docker-compose build

**to run container**

docker run -i -t -v c:/Projects/jaspr/app:/app -p 5000:5000 -e FLASK_APP=hello.py -w /app --rm cdcflu/jaspr:v1

## Other Notes/random stuff

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

docker run -i -t  -v c:/frunk:/frunk -p 8888:8888 continuumio/anaconda3 /bin/bash -c "/opt/conda/bin/conda install jupyter -y --quiet && mkdir /opt/notebooks && /opt/conda/bin/jupyter notebook --notebook-dir=/opt/notebooks --ip='\*'  --no-browser --allow-root

I get the error:
docker: Error response from daemon: driver failed programming external connectivity on endpoint flamboyant_kepler (caadd7788899e6a680608e91274e185cd29a077a0c85f016a209ad2c125669e0): Error starting userland proxy: mkdir /port/tcp:0.0.0.0:8888:tcp:172.17.0.2:8888: input/output error.
[SOLVED]It seems that the problem goes away when I restart docker.  

[PROBLEM]  cannot run Jupyter by using container name as host
[SOLVED] You need to specify localhost:8888
