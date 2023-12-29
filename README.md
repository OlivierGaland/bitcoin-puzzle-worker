# bitcoin-puzzle-worker
Client side of bitcoin puzzle challenge :  
This software will allow you to participate in Bitcoin Puzzle Challenge by scanning random ranges and sending results to the pool server, once a challenge is completed the reward will be shared regarding the ranges count of all participants and distributed.

1. Bitcoin Puzzle challenge overview :  
This challenge has been introduced in 2015. Someone has dispatched around 1000 BTC among 160 public addresses with the information that private key associated are in a specific range (from 1 to 160 bits), up to anyone to find those private key and transfer the BTC on his own wallet.  
Currently many of those private keys have been found, and at the time of writing the current private key to find are on 66 bits and more. Some keys above 66 bits have been found (70, 75, 80, 85 and so on) thanks to a send transaction from those wallet done by the puzzle creator, this allow to reveal the public key and open the challenge to a more efficient method than brute force (pollard-kangaroo algorithm).  
The provided software focus on brute force only, thus keys that cannot be divided by 5. For more detailed infos on the challenge see [current state](https://privatekeys.pw/puzzles/bitcoin-puzzle-tx) and [thread on bitcointalk.org](https://bitcointalk.org/index.php?topic=5218972).  
It is unclear why this challenge has been created. One obvious answer will be to prove by proposing big rewards ($280,000 to $640,000 per challenge) that given a public address, it is impossible to find the private key. Using increasingly difficult keys will give an idea of the current safety of a wallet with our today compute power. Actually 64 bits key has been broken with brute force, and 125 bits key that unveiled public key has also been broken using the pollard-kangaroo algorithm. A 256 bits private key is actually totally out of scope for those methods.    

2. How does it works ? What do I need to participate ?  
The software to run on your side is in this package, it is a docker stack to set up (tested on Windows and Linux). If you want to start from scratch, basically you need a computer with one or more Nvidia video cards, install linux, nvidia drivers, docker and install this software.  
Typically if you own crypto-mining nvidia-based hardware, it can be easily converted to run this software, but you can also run it on your windows computer by installing docker desktop.  
Currently only Nvidia cards are supported, I will think about adding AMD cards support if possible.

3. If you want to participate, some information you want to know :  
    * Brute force method for breaking 66+ bit keys is very consuming regarding time and power, keep in mind even if the reward for breaking a key is around $300,000 (with a $40,000 BTC) it can be not profitable in area where the electricity cost is very expensive.  
    * Pool truthfulness is important : there is no way to guarantee that you will get paid. You should rely on my premise and the fact you know my real name and location.  
    * As this is a challenge, there maybe other people trying to break the same key, so if one lonely lucky people find it all the pool work done will become useless. This is why I didn't included the 66 bit challenge in the pool as I know from bitcointalk.org that some people are currently working on this since several monthes.  
    * The rewards sharing will be following : 10% will go to the pool management for dev/maintainment costs, 90% will be shared among the workers regarding the block count they scanned. I may open a thread if some want a different sharing model (like giving a bonus for the worker that discovered the key).  
    * The software is currently still under developpement and may be improved, so it is not bug-free. I'm testing it at home with my personal computer (1x3060Ti + windows) and on my mining rig (6x3060Ti + linux)  

## Table of contents

1. [Installation](#install)
2. [Setup](#setup)
3. [GUI Manual](#manual)
4. [FAQs](#faqs)
5. [GUI Screenshots](#screenshots)

## Installation

1. Windows OS pre-requisites :  
    * From an already installed windows computer with nvidia drivers you just need to install [docker-desktop](https://www.docker.com/products/docker-desktop/)

2. Linux OS pre-requisites (use provided version if possible, unless you want to experiment):  
    * Create an usb stick and install a new fresh OS [Ubuntu server 22.04.3 LTS](https://ubuntu.com/download/server#downloads)
    * Install nvidia drivers :
        ```bash
        sudo add-apt-repository ppa:graphics-drivers/ppa
        sudo apt-get install dkms build-essential
        sudo apt-get update
        sudo apt list nvidia-driver*                          # list available drivers
        sudo apt install nvidia-driver-535-server             # i'm using nvidia-driver-535-server
        sudo reboot now                                       # reboot
        nvidia-smi                                            # verify installation (it should display all your plugged gpus)
        ```       
    * Install [Docker](https://docs.docker.com/engine/install/ubuntu/) :
        ```bash
        # remove packages
        for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done     
        # add Docker's official GPG key
        sudo apt-get update                                                                                                                   
        sudo apt-get install ca-certificates curl gnupg
        sudo install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        sudo chmod a+r /etc/apt/keyrings/docker.gpg
        # add repository to apt sources and install docker
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        sudo apt-get update
        sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        # verify installation (command should display help)
        sudo docker
        sudo docker-compose
        ```       

3. Install [Portainer](https://www.portainer.io/) :
    * This is optional but recommended as Portainer is a very good browser tool for managing containers running on your host
    * On Linux bash or Windows powershell (remove sudo from commands on Windows) :
        ```bash
        sudo docker volume create portainer_data
        sudo docker run -d -p 8000:8000 -p 9443:9443 -p 9000:9000 --name portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:latest
        ```       
    * Open your browser on http://localhost:9000/ , set your admin password and select local environment        

4. Download the worker :
    * On Linux bash or Windows powershell, cd to the directory that will store the worker.
    * Download from github
        ```bash 
        git clone https://github.com/OlivierGaland/bitcoin-puzzle-worker
        ```       

## Setup

1. Setting up docker-compose.yml :  

2. Setting up .env file :  

3. Setting up .env.gpu files :  

4. Starting the stack :  
        ```bash 
        sudo docker-compose up -d
        ```       



## FAQs

Currently on dev, manual will be available soon

## GUI Screenshots

![image](https://github.com/OlivierGaland/bitcoin-puzzle-worker/assets/26048157/eef50be8-d7a4-4de4-a5d7-c040221404f0)
![image](https://github.com/OlivierGaland/bitcoin-puzzle-worker/assets/26048157/52790a41-5b31-42ad-8039-e9b39797fded)
