Instructions for executing docker-compose build && docker-compose down && docker-compose up

In QA: build/docker/dockerfile-jaspr

Disable line 6: # RUN apt-get --allow-releaseinfo-change update

In PROD: 

Enable line 6: RUN apt-get --allow-releaseinfo-change update