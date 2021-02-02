# rhasspy-matrixvoice-python-iobroker
rhasspy and MATRIX Voice board based speech recognition with intent handling in python and ioBroker connection

## Prerequisites

* 2 Raspberry Pi 3 or higher with docker environment
* [MATRIX Voice](https://www.matrix.one/products/voice) microphone array board installed on one (the slave or front-end) Pi

## Setup

* adjust config.json according to local settings/capabilities
* master Pi: 
```
./install.sh image
./install.sh run
```
* slave Pi: 
```
./install.sh image
./install.sh matrixvoice1
./install.sh matrixvoice2
./install.sh run
```
