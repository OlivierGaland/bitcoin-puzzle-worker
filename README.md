# bitcoin-puzzle-worker
Client side of bitcoin puzzle challenge : This software will allow you to participate in Bitcoin Puzzle Challenge by scanning random ranges and sending results to the pool server, once a challenge is completed the reward will be shared regarding the ranges count of all participants and distributed.

1. Bitcoin Puzzle challenge :
 This challenge has been introduced in 2015. Someone has dispatched around 1000 BTC among 160 public addresses with the information that private key associated are in a specific range (from 1 to 160 bits), up to anyone to find those private key and transfer the BTC on his own wallet.
 Currently many of those private keys have been found, and at the time of writing the current private key to find are on 67 bits and more.
 Some keys above 67 bits have been found (70, 75, 80, 85 and so on) thanks to a send transaction from those wallet done by the puzzle creator, this allow to reveal the public key and open the challenge to a more efficient method than brute force (pollard-kangaroo algorithm).
 The provided software focus on brute force only, thus keys that cannot be divided by 5.
 For more detailed infos on the challenge see [current state](https://privatekeys.pw/puzzles/bitcoin-puzzle-tx) and [thread on bitcointalk.org](https://bitcointalk.org/index.php?topic=5218972).

2. How does it works ? What do I need to participate ?
 The software to run on your side is in this package, it is a docker stack to set up (tested on Windows and Linux). If you want to start from scratch, basically you need a computer with one or more Nvidia video cards, install linux, nvidia drivers, docker and install this software.
 Typically if you own crypto-mining nvidia-based hardware, it can be easily converted to run this software, but you can also run it on your windows computer by installing docker desktop.

## Installation

Currently on dev, manual will be available sonn

