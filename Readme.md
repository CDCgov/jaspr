# JASPR
JASPR calculates titers from logistic fits on resistance assay data.
Access JASPR at https://jaspr.biotech.cdc.gov/

# Getting Started
Instruction on how to get the project up and running.

# Prerequisites
Need to have podman and podman-compose installed on your machine.

# Branch Strategy
# master -- This is deployed on jaspr's PROD and QA servers 
-- This is the primary branch on jaspr-prod: id-jaspr-prod-02.biotech.cdc.gov

# jaspr_qa 
-- This is the QA branch used for testing

# Any bug fixes or feature add should be developed in a new branch. 
Create your new branch based on the master branch. 
Once your branch is ready for testing, merge it into the QA branch and deploy it to the jaspr-qa server: id-jaspr-qa-01.biotech.cdc.gov
 
Once testing on the QA branch is approved, merge the QA branch to master but make sure to not close/delete the QA branch.

Then, update the jaspr-prod server with master branch.

# Testing
Placeholder for any notes for any future automated testing

# Deployment
The production server and deployment is based on the master branch. 

# NOTE: Starting the containers
cd ../../../var/JASPR
podman-compose build && podman-compose down && podman-compose up

# Adding new features to JASPR

# git branch -a
>   master
>  *qa
> 

# Pull the latest master branch to your local environment
git fetch origin master

# Make new 'feature' branch off of master
# git branch <new-branch> <base-branch>

git branch feature master

# Make all changes to new feature branch, 
# verify things are working as expected on feature branch

# Update changes from feature branch onto qa branch
# checkout to jaspr_qa branch, then merge changes from feature branch

git checkout jaspr_qa
git merge feature

# verify things are working as expected on jaspr_qa branch
# push changes to BitBucket
git push origin jaspr_qa

LOG IN to the jaspr-qa environment: id-jaspr-qa-01.biotech.cdc.gov

# pull jaspr_qa branch to jaspr-qa environment
sudo su jaspr
cd ~ 
pwd
ls
cd jaspr

# move to master branch
git checkout master

# pull jaspr_qa from Bitbucket
git fetch origin jaspr_qa:jaspr_qa

# move to jaspr_qa branch
git branch
git checkout jaspr_qa

# verify new feature is working as expected in jaspr_qa
# checkout to master branch, then merge changes from jaspr_qa branch

git checkout master
git merge qa

# verify things are working as expected on master branch
# push changes to origin

git push origin master

# LOG IN to jaspr-prod server: id-jaspr-prod-01.biotech.cdc.gov
# pull master branch to jaspr-prod environment

git checkout jaspr_qa
git fetch origin master
git checkout master

sudo su jaspr
cd ~ 

cd jaspr_qa/build
podman-compose build && podman-compose down && podman-compose up

# Conduct feature and regression testing to verify things are working as expected.
