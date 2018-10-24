---
title: Developer Notes

Creating HTML Version of this file
---

* * *

To create the HTML version of these notes install pandoc from <https://pandoc.org> and then use the batch file _createhtmldocs.bat_ to generate an HTML file


******
export FLASK_APP=jaspr
If you are outside of the project directory make sure to provide the exact path to your application directory. Similiarly you can turn on “debug mode” with this environment variable:

export FLASK_DEBUG=true
In order to install and run the application you need to issue the following commands:

pip install -e .
flask run
************


## Next Steps

1.  [x] Set up a basic template for the main page
2.  [x] Add bootstrap and break out basic page layout
3.  [x] Add basic color scheme so it isn't ugly
4.  [x] Add file upload function (flask-uploads)
5.  [x] Remove CDN from graphing
6.  [x] Load data into Pandas
7.  [x] Set up a graph page using Bokeh
8.  [x] Put data table into tab (temporary)
9.  [x] Connect data grid to graph
10. [x] fix Juypter to restart from old or recreate
11. [x] create stubbed out API and wire up to prototype
12. [x] Wire in old help content
14. [x] Establish classes for data and load them in for use
15. [x] Wire in multi sample list
16. [x] Wire up individual charts and data
17. [x] Flesh out calls to base service tier
18. [x] Wire in grabbing data for each sample separately
13. [ ] Hook up the excel file reading functionality from legacy application
19. [ ] Add custom x axis labels for titers
20. [ ] Add cp50 and cp90 labels
21. [ ] Flesh out settings form
22. [ ] Add configuration (yaml)
23. [ ] Add report file creation functionality
24. [ ] Add validation so that only xslx files can be uploaded
25. [ ] Add Flask configuration file

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
