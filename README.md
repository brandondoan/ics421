# Assignment 1: DDL Processing for a Parallel DBMS

This project was an attempt to implement a parallel SQL processing system. The system is capable of handling a large cluster of 
DBMS instances running accross multiple servers. The DDL processor is capable of taking DDL statements and executing them across the 
cluster of DBMS's in parallel. The machine that runs the DDL Processor will also create and maintain a catalog database which 
contains every table within the DBMS cluster as well as the location of where it is stored. Each server is able to process any query
sent, and updates its unique database. After any successful query, the server then sends a confirmation back to the DDL processor.

## Getting Started


These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 
In this version, the project is not ready for live systems. As of now, testing can be done with the use of docker containers.

### Prerequisites

Cloning this repo to your machine

Docker (Virtualization)

A linux environment with the following packages

* iputils-ping
* iproute
* dnsutils

Python3 with the following packages
 
* python3-pip
* sqlite3

Text Editor of your choice


### Installing

Below are the step by step instructions on how to get your development environment started. For the purpose of clarity, included with the instructions are examples of what the command line prompt should look like. 

You can clone this repo by using 'https://github.com/brandondoan/ics421'

Install Docker onto your computer

* Download Docker Community Edition from the following link, [Docker Website](https://www.docker.com) 
    * Windows users that are having trouble, can instead download Docker Toolbox at this link, [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)
    * Follow the installation instructions provided at, [Getting Started], (https://docs.docker.com/get-started/)
    
After downloading docker we can now setup our containers with the ubuntu image. To do this we have to open up a terminal and type in the following command.

```
docker run -it --name=<container name> ubuntu
```

We now have a docker container with the linux environment setup! Unfortunately the base ubuntu image is missing a few packages that we will require for our program. To install the packages type in the following commands.

```
apt-get -y update
apt-get -y install iputils-ping
apt-get -y install iproute
apt-get -y install dnsutils
```

After installation of the packages are complete, the next step is to setup python and its package installer. Use the following commands to install.

```
apt-get -y install python3
apt-get -y install python3-pip
```
The next package to install is sqlite3, the the command for install is.

```
apt-get -y install sqlite3
```

You can also install a text editor of your choice. Here is an example of how to install vim.

```
apt-get -y install vim
```

From here you should change from the root account to a user account, you must create a new user account and login to it.

```
adduser <username>
su <username>
```

After switching over to the new user account, go to your home directory and then create a directory that you wish to copy your files over to.

```
cd
mkdir <directory name>
cd <directory name>
```

We can now exit docker to copy over the files in the repository we cloned.

```
exit
```

Change directory to the location of your cloned repository. Then type in the following into the command prompt. (Will only work properly if you are in the directory where the files are located)

```
docker cp <filename> <docker container name>:/home/<username>/<directory name>/<filename>
```

Repeat this process with every file in the repository. 

You are now able to test the parDBD.py server program and runDDL.py client program on a single machine. In order to run the tests across multiple machines, create additional containers that contain the parDBD.py file. 

## Running the tests

Explain how to run the automated tests for this system


## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
