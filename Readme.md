JASPR
JASPR calculates titers from logistic fits on resistance assay data.

Getting Started
Instruction on how to get the project up and running.

Potentially more thorough instructions should be created but there is a start available here: install.md

Prerequisites
Need to have docker and docker-compose installed on your local dev machine.

Branch Strategy
Core branches - master -- This is deployed on disc-prod - QA -- This is the primary branch on disc-qa

Any bug fixes or feature add should be developed in a new branch. Create your new branch based on the master branch. Once your branch is ready for testing, merge it into the QA branch and deploy it to disc-qa. Once testing on the QA branch is approved, merge the QA branch to master but make sure to not close/delete the QA branch.

Testing
Placeholder for any notes for any future automated testing

Deployment
The production server and deployment is based on the master branch. 
1. For deployment in the disc project root folder on the server make sure that you have the current commit of the master branch. - IE git pull 
2. Run a docker-compose down, build (no-cache), and up (detached) - IE docker-compose down && docker-compose build --no-cache && docker-compose up -d 
3. Deployment is complete-- check server url to ensure things are up and running as expected.

Instructions for executing docker-compose build && docker-compose down && docker-compose up

In QA: build/docker/dockerfile-jaspr
Disable line 6: # RUN apt-get --allow-releaseinfo-change update

In PROD: 
Enable line 6: RUN apt-get --allow-releaseinfo-change update