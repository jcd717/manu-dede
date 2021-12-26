#!/bin/sh
# génère le fichier requirements.txt

pipenv run pip freeze -l > requirements.txt
