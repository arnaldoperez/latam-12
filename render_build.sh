#!/usr/bin/env bash
# exit on error
set -o errexit

npm install
npm run build

pipenv install
cp /etc/secrets/firebase_credentials.json ./firebase_credentials.json

if [ !  -d "migrations" ];
then
    echo "NO MIGRATIONS"
    pipenv run init
fi
echo "UPDATING MIGRATIONS"
pipenv run migrate && 
pipenv run upgrade 