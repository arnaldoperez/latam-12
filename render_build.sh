#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build

pipenv install
cp /etc/secrets/firebase_credentials.json ./firebase_credentials.json

if [ -d "migrations" ];
then
    pipenv run migrate && 
    pipenv run upgrade 
else
    pipenv run init
	pipenv run migrate && 
    pipenv run upgrade 
fi