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

A linux environment with the following packages

* iputils-ping
* iproute
* dnsutils

Python3 with the following packages
 
* python3-pip
* sqlite3

Text Editor of your choice

Docker (Virtualization)

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Give the example
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
