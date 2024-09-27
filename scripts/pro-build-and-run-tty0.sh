#! /bin/bash

if [[ $PWD/ = */scripts/ ]]; then
    echo "Script must be executed form root directory, script will now exit!"
    exit 1
fi

sudo apt update -y

if ! command -v node &> /dev/null; then
    echo "Node is not installed, installing..."
    sudo apt install nodejs -y
else
    echo "Node already installed"
fi

if ! command -v npm &> /dev/null; then
    echo "Npm is not installed, installing..."
    sudo apt install npm -y
else
    echo "Npm already installed"
fi

cd frontend

npm i
npm run build

cd ../

mv ./frontend/build ./static

sudo docker-compose up --build app-pro