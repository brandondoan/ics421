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

Install Docker onto your computer

* Download Docker Community Edition from the following link, [Docker Website](https://www.docker.com) 
    * Windows users that are having trouble, can instead download Docker Toolbox at this link, [Docker Toolbox](https://docs.docker.com/toolbox/toolbox_install_windows/)
    * Follow the installation instructions provided at, [Getting Started], (https://docs.docker.com/get-started/)
    
After downloading docker we can now setup our containers with the ubuntu image. To do this we have to open up a terminal and type in the following command.

```
docker run -it --name=<container name> ubuntu
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc
