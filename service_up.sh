#!/bin/bash

cd /home/dkarpov/projects/self/rocket/
#cd /home/dockeruser/viruslib_client
chown -R 1000:1000 /home/dkarpov/projects/self/rocket/parsing_results/category

/usr/local/bin/docker-compose up -d --remove-orphans
#/usr/bin/docker-compose up -d --remove-orphans

