#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build

pipenv install
cp /etc/secrets/firebase_credentials.json ./firebase_credentials.json

pipenv run init
pipenv run migrate
pipenv run upgrade
