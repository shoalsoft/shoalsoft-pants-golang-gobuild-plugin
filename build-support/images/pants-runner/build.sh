#!/bin/bash
docker build . -t pants-runner:latest -t registry.gitlab.com/tdyas/shoalsoft-pants-golang-plugin/pants-runner:latest
docker push registry.gitlab.com/tdyas/shoalsoft-pants-golang-plugin/pants-runner:latest
