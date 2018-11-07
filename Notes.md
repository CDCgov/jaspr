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

1.  [x] Flesh out settings form ui
2.  [ ] Style the import screens
3.  [ ] Wire up the settings form functionality
4.  [ ] Deploy the application to the linux box
5.  [ ] Get a linux account for Garrett and access to the box
6.  [ ] Code sweep, clean Todos
7.  [ ] Code sweep, clean comments
8.  [ ] Add configuration loading (json)
9.  [ ] Add configuration saving
10. [ ] Add validation to basic imports
11. [ ] create imports as a plugin and add excel
12. [ ] Add xslx import functionality
13. [ ] update help page functionality
14. [ ] Add report file creation functionality
15. [ ] Add ability to create PNG images of graphs
16. [ ] Move import, report and image generation to web service calls

## Creating and Running the jaspr project container for development

**Using provided Python tooling**

This project is designed to be developed using a Docker container as a running environment.  The dos commmand file to create this container is _jasprbuild.cmd_ and a linux bash version is called _jasperbuild.sh_.  Here are the instructions to use this tool:

    jasprbuild.cmd

    This will build and run the jaspr software within
    a docker container

    /b to build the container
    /r to run the container
    /j to run a jupyter container
    /c to run the container and stop in bash shell

## Other Notes/random stuff
