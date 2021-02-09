#!/bin/bash

HOST=$(hostname -s)
IMAGE=rhasspy/rhasspy

function do_image {
    docker pull ${IMAGE}
}

function docker_run {
    docker run $* \
        -e TZ=Europe/Berlin \
        -v "$HOME/.config/rhasspy/profiles:/profiles" \
        --net host \
        --name rhasspy \
        ${IMAGE} \
        --profile de \
        --user-profiles /profiles
}

function do_matrixvoice1 {
    curl https://apt.matrix.one/doc/apt-key.gpg | sudo apt-key add -
    echo "deb https://apt.matrix.one/raspbian $(lsb_release -sc) main" | sudo tee /etc/apt/sources.list.d/matrixlabs.list
    sudo apt-get update -y
    sudo apt-get upgrade -y
    sudo reboot
}

function do_matrixvoice2 {
    sudo apt install -y matrixio-kernel-modules
    sudo apt-get install -y matrixio-creator-init libmatrixio-creator-hal libmatrixio-creator-hal-dev git python3-pip
    pip3 install --user matrix-lite
    sudo reboot
}

function do_test {
    docker_run --rm -it $(get_args $1)
}

function do_stop {
    docker rm -f rhasspy
}

function do_restart {
    do_stop
    sleep 5
    do_run $1
}

function do_run {
    slave=$(jq .rhasspy.slave.host config.json | sed -e 's/"//g')
    if [ "${HOST}" = "${slave}" ]
    then
        docker_run -d --restart=unless-stopped --device /dev/snd:/dev/snd
    else
        docker_run -d --restart=unless-stopped
    fi
}

function do_backup {
    timestamp=$(date +'%Y-%m-%d_%H%M')
    tar -C ${HOME}/.config -c -z -f /backup/${HOST}/${timestamp}_rhasspy.tar.gz rhasspy
}

task=$1
shift
do_$task $*
