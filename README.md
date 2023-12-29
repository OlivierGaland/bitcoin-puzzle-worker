# bitcoin-puzzle-worker
Client side of bitcoin puzzle challenge : This software will allow you to participate in Bitcoin Puzzle Challenge by scanning random ranges and sending results to the pool server, once a challenge is completed the reward will be shared regarding the ranges count of all participants and distributed.

1. Bitcoin Puzzle challenge overview :  
This challenge has been introduced in 2015. Someone has dispatched around 1000 BTC among 160 public addresses with the information that private key associated are in a specific range (from 1 to 160 bits), up to anyone to find those private key and transfer the BTC on his own wallet.  
Currently many of those private keys have been found, and at the time of writing the current private key to find are on 66 bits and more. Some keys above 66 bits have been found (70, 75, 80, 85 and so on) thanks to a send transaction from those wallet done by the puzzle creator, this allow to reveal the public key and open the challenge to a more efficient method than brute force (pollard-kangaroo algorithm).  
The provided software focus on brute force only, thus keys that cannot be divided by 5. For more detailed infos on the challenge see [current state](https://privatekeys.pw/puzzles/bitcoin-puzzle-tx) and [thread on bitcointalk.org](https://bitcointalk.org/index.php?topic=5218972).  

2. How does it works ? What do I need to participate ?  
The software to run on your side is in this package, it is a docker stack to set up (tested on Windows and Linux). If you want to start from scratch, basically you need a computer with one or more Nvidia video cards, install linux, nvidia drivers, docker and install this software.  
Typically if you own crypto-mining nvidia-based hardware, it can be easily converted to run this software, but you can also run it on your windows computer by installing docker desktop.  

3. If you want to participate, some information you want to know :  
Brute force method for breaking 66+ bit keys is time and power consumming, keep in mind even if the reward for breaking a key is around $300,000 (with a $40,000 BTC) it can be not profitable in area where the electricity cost is very expensive.  
Pool truthfulness is important : there is no way to guarantee that you will get paid. You should rely on my premise and the fact you know my real name and location.  
As this is a challenge, there maybe other people trying to break the same key, so if by chance one of those people find it, all the pool work done will become useless. This is why I didn't included the 66 bit challenge in the pool as I know from bitcointalk.org that some people are working on this one since several monthes.  
The rewards sharing will be following : 10% will go to the pool management for dev/maintainment costs, 90% will be shared among the workers regarding the block count they scanned. I may open a thread if some want a different sharing model (like giving a bonus for the worker that discovered the key).  
The software is currently still under developpement and may be improved, so it is not bug-free. I'm testing it at home with my personal computer (1x3060Ti + windows) and on my mining rig (6x3060Ti + linux)  

## Table of contents
1. [Installation](##install)
2. [Setup](##setup)
3. [GUI Manual](##setup)
4. [FAQs](##faqs)
5. [GUI Screenshots](##screenshots)

##install

##faqs

Currently on dev, manual will be available soon

![image](https://github.com/OlivierGaland/bitcoin-puzzle-worker/assets/26048157/eef50be8-d7a4-4de4-a5d7-c040221404f0)
![image](https://github.com/OlivierGaland/bitcoin-puzzle-worker/assets/26048157/52790a41-5b31-42ad-8039-e9b39797fded)
