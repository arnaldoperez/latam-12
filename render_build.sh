#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build

pipenv install
cp /etc/secrets/firebase_credentials.json ./firebase_credentials.json
pwd
ls

pipenv run reset_db
