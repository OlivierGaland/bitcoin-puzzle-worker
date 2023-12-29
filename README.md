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
    * The rewards sharing will be following : 10% will go to the pool management for dev/infrastructure costs, 90% will be shared among the workers regarding the block count they scanned. I may open a thread if some want a different sharing model (like giving a bonus for the worker that discovered the key).  
    * The software is currently still under developpement and may be improved, so it is not bug-free. I'm testing it at home with my personal computer (1x3060Ti + windows) and on my mining rig (6x3060Ti + linux)  

## Table of contents

1. [Installation](#installation)
2. [Setup](#setup)
3. [GUI Manual](#guimanual)
4. [FAQs](#faqs)
5. [GUI Screenshots](#guiscreenshots)

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
    * Open your browser on http://localhost:9000/ , set your admin password and select local environment, the software is now ready    

4. Download the worker suite :
    * On Linux bash or Windows powershell, cd to the directory that will store the worker.
    * Download from github
        ```bash 
        git clone https://github.com/OlivierGaland/bitcoin-puzzle-worker
        ```       

## Setup

1. Setting up docker-compose.yml :  
    - The repository contains 2 docker-compose.yml examples, one for my windows computer (1 GPU) et one for my linux computer (6 GPU), take some time to review the first one and build your own and name it docker-compose.yml
    - There are 2 services type :
        * the watchdog that will monitor stack health and provide a web browser graphical interface at http://localhost. It will check for faulty containers and restart them if possible for instance
        * the clients that will run the scanning software, each client is associated with one video card, so there will be as many clients as you have video cards on your rig.
    - watchdog setup :
        * depends_on : you should add one line depends_on per client with the client service name
        * env_file : add your env.watchdog file name on this line
    - client setup :
        * service name should be somewhat standardized, keeping the current policy is advised, for instance bitcrack-client-00 for gpu 0 (note the 2 digits in the service name that allow a smooth sorting by name)
        * image : use image ogaland/bitcoin-puzzle-bitcrack:ccXX were XX is the compute capability of the associated gpu. You can find this information on [nvidia site](https://developer.nvidia.com/cuda-gpus), for instance a 3060Ti is compute capability 8.6, this means you should use in this case image ogaland/bitcoin-puzzle-bitcrack:cc86. All generated images are available at [dockerhub](https://hub.docker.com/repository/docker/ogaland/bitcoin-puzzle-bitcrack/general). If it does not exist you should drop a message to ask me to generate it.
        * env_file : it is also strongly advised to keep current name policy, for instance .env.gpu.00 for gpu associated with bitcrack-client-00
        * device_ids : there should be only one id, and for clarity use the number in the service name, for instance bitcrack-client-00 will be for device_ids ['0']


2. Setting up .env file :  
    - WATCHDOG_EXPOSED_PORT : you can change it if you want to use another port to access the Watchdog UI on your browser (80 is default)

3. Setting up .env.watchdog :  
    - There are two .env.watchdog examples in the repository, one for my windows computer (1 GPU) et one for my linux computer (6 GPU), take some time to see what are inside. 
    - WORKER_GPU_COUNT : this value should be the number of gpu installed on your rig, this will allow the watchdog to know how many clients and gpus are supposed to be online.
    - GPU_MEM_CLOCK_xx : optional and not working on windows, delete if not needed, this will set memory clock for gpu xx, for instance GPU_MEM_CLOCK_00 for gpu device_id '0'
    - GPU_POWER_LIMIT_xx : optional and not working on windows, delete if not needed, this will set power limit for gpu xx, for instance GPU_POWER_LIMIT_00 for gpu device_id '0' 

4. Setting up .env.gpu files :  
    - There should be one .env.gpu file per gpu installed on your rig, please keep naming convention .env.gpu.xx where xx is a 2-digit number matching client service name
    - Worker settings :
        - WORKER_START_DELAY : this will set a waiting time (in sec) before the client start, during my testing it seems if all clients are started in sync, nvidia drivers does not appreciate and may crash some containers, to prevent that use a different WORKER_START_DELAY for each .env.gpu file, a delay of 10 sec between each delay seems enough.
        - POOL_NAME : The pool name to work in.
        - WORKER_NAME : This should be a bitcoin address and will be checked on server side, note only legacies addresses are accepted (starting with 1 or 3). Be aware that it will be the proof that you had processed assigned range. Once the target key is broken, the rewards will be sent to this address. So be sure to not lose access to this wallet in any case.
        - SERVER_IP : should be set to  -------
        - SERVER_PORT : should be set to  -------
    - Video card settings :
        TODO
    - Filter settings :
        TODO



5. Starting the stack :  
        ```bash 
        sudo docker-compose up -d
        ```       



## FAQs

Currently on dev, manual will be available soon

## GUI Screenshots

![image](https://github.com/OlivierGaland/bitcoin-puzzle-worker/assets/26048157/eef50be8-d7a4-4de4-a5d7-c040221404f0)
![image](https://github.com/OlivierGaland/bitcoin-puzzle-worker/assets/26048157/52790a41-5b31-42ad-8039-e9b39797fded)
