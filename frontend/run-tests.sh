#!/bin/bash
cd "$(dirname "$0")"
export NODE_OPTIONS='--experimental-vm-modules'
./node_modules/.bin/jest --config=jest.config.js --ci --coverage --maxWorkers=2 "$@"
