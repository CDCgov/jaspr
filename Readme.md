## Notices

### Contact Info

ORG: NCIRD
Contact Email: ddidncirdflulimsdevelopers@cdc.gov
Version: 12.5
Contract#: 75D30122F15368

### Public Domain Standard Notice

This repository constitutes a work of the United State Government and is a private repository.  Requests for this information can be made at shareit@cdc.gov.

### Contributing Standard Notice

JASPR calculates titers from logistic fits on resistance assay data.
Access JASPR-PROD at https://jaspr.biotech.cdc.gov/ and JASPR-QA at https://jaspr-qa.biotech.cdc.gov/

## JASPR


### License Standard Notice

The current configuration of JASPR runs in Podman containers on RHEL8 OS VMs hosted by SciComp.

### Branch Strategy Notice

Core branches
- master -- This is deployed in the production environment
- jaspr_qa -- This is the primary branch in the QA environment

sudo su jaspr
cd ~ 
pwd
ls
cd jaspr

This is the primary branch on jaspr-prod: id-jaspr-prod-02.biotech.cdc.gov
Any bug fixes or feature add should be developed in a new branch. Create your new branch based on the `master` branch. 

Once your branch is ready for testing, merge it into the `QA` branch and deploy it to the QA environment. 

Create your new branch based on the master branch. 
Once your branch is ready for testing, merge it into the QA branch and deploy it to the jaspr-qa server: id-jaspr-qa-01.biotech.cdc.gov
 
Once testing on the QA branch is approved, merge the QA branch to master but make sure to not close/delete the QA branch.

Then, update the jaspr-prod server with master branch.

cd ../../../var/JASPR
podman-compose build && podman-compose down && podman-compose up

=======





