# Assignment 2: Naive SQL Processing for Parallel Database

This project contained two parts, the first was an attempt to implement a naive parallel SQL processing system(runSQL.py). The system is capable of handling a large cluster of DBMS instances running accross multiple servers. The DDL processor is capable of taking DDL statements and executing them across the cluster of DBMS's in parallel. The machine that runs the DDL Processor will also create and maintain a catalog database which contains every table within the DBMS cluster as well as the location of where it is stored. Each server is able to process any query sent, and updates its unique database. After any successful query, the server then sends a confirmation back to the DDL processor as well as the relevant rows within the database assocciated with the query. Which in turns prints out all rows and their corresponding node, and finally prints a notification if the catalog database was updated or not.

The second part of the project was to implement a parallel loader(loadCSV.py) capable of reading csv files and loading the values into the appropriate nodes dependant on the partition method. The loader uses a config file to determine the node addresses as well as the partition method and parameters. From that information it divides the values from the csv file into seperate queries according the the parameters and then submits the queries to each database. Upon completion, will update the catalog database if necessary as well as print the amount of rows sent to each node, and a notification when the catalog database is updated.

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

You are now able to test the parDBD.py server program and runSQL.py client program and the loadCSV.py parallel loader on a single machine. In order to run the tests across multiple machines, create additional containers that contain the parDBD.py file. 

## Editing the files

Before we can actually run the tests we will have to reconfigure our clusterconfig.ini. and parDBD.py. This is a sample of the contents within the config file.

### Sample contents of clusterconfig.ini file
```ini
[catalog]
driver: com.ibm.db2.jcc.DB2Driver
hostname: 172.17.0.2:50001/mycatdb
ip: 172.17.0.2

[nodecount]
numnodes: 2

[node 1]
driver: com.ibm.db2.jcc.DB2Driver
hostname: 172.17.0.3:50001/mydb1
ip: 172.17.0.3
param1: 1
param2: 1235

[node 2]
driver: com.ibm.db2.jcc.DB2Driver
hostname: 172.17.0.4:50001/mydb2
ip: 172.17.0.4
param1: 1236
param2: 2500

[BOOKS]
method: range
column: isbn

[MOVIES]
method: hash
column: serial
param1: 2
```
We will need to adjust the values according to the ip addresses of your own containers. We will also need to add or remove nodes depending on how many servers we are running. To find the ip address of your container you can type into the command prompt. 

```ip a```

Mark down the ip address, which container it belongs to, and the node number, as they will be used to update your clustercfg.ini and parDBD.py file. After finding the ip address for each container edit your config file accordingly, adding or removing nodes depending on the amount of servers you intend to run. Making sure that your catalog section contains the ip address that you will be running runSQL.py (your client program) from. In your nodecount section, update the value of numnodes to match the amount of nodes you are using. For every table within your databases you will need to create a section that contains the partition method and partition column. The partition parameters for a range method can be stored in your nodes, but be careful that for each table with a range method, you will need to create new unique partition parameters with unique id's. If the method is hash, you can store the partition parameter in the same section.

Next on each container you must update the parDBD.py file on line 5, to the correct database name based on the node number, i.e. 'mydb1.db'  for node 1 and 'mydb2.db' for node 2, etc...

### First 6 lines of code in parDBD.py
```python
import socket
import sys
import sqlite3

connection = sqlite3.connect("mydb1.db") #object for connection to sqlite3 database for this server
cursor = connection.cursor() #cursor to execute DDL commands to database
```
## Running tests for runSQL.py

We are now finally ready to test our DDL processor and DBMS servers. The file, ddlfile.sql, contains a generic DDL statement that we can use for our test.

### Sample content of ddlfile.sql file
```sql
CREATE TABLE BOOKS(isbn char(14), title char(80), price
decimal);
```

On each container we have to run the parDBD.py program in the background to listen for queries. The program takes two command line arguments: Ip address or hostname, and the port number(by default I have the port numbers set to 50001, if you want to change this you will also need to update the port number in the runSQL.py file). An example of the command is shown below.

```
python3 parDBD.py <IP or hostname> <port number> &
```
After all the containers have parDBD.py running we can then execute our runSQL.py program on our container that is acting as the client. The runSQL.py program takes two command line arguments: the clusterconfig file, and the ddlfile file. An example on how to run the program is shown below

```
python3 runSQL.py clusterconfig.ini ddlfile.sql
```
During the execution of the runSQL.py file, the client will check to see if the catalog database exists locally, if it does not it will create a local database that contains a SQL table, that catalogs where tables are stored in the DBMS as well as at which node. Then it sends its DDL query to the server machines in parallel and waits for a response.

After execution each server that is sent the query will print out a confirmation message with the query included. It will then process the query and update its local database. In the event that the query succeeds, it will return to the server a confirmation that the query succeeded, on the other hand if the query failed, it will return a failure notice.

Upon receiving the success/fail notice the client will update the catalog if needed, and afterwards will print out a success/fail report for every query sent to each server. It will also print a statement of whether the catalog database was updated as well. 

### Sample outputs of runSQL.py execution

```
1234 "Ender's Game" 7.99
1235 "Speaker for The Dead" 7.99
1236 "Xenocide" 7.99
172.17.0.3:50001/mydb1 ddlfile.sql Success
172.17.0.4:50001/mydb2 ddlfile.sql Success
172.17.0.2:50001/mycatdb.db ddlfile.sql catalog updated.
```
```
172.17.0.3:50001/mydb1 ddlfile.sql Failure
172.17.0.4:50001/mydb2 ddlfile.sql Failure
172.17.0.2:50001/mycatdb.db ddlfile.sql catalog had no updates.
```

### Sample outputs and error conditions of parDBD.py query processing

```
Server: Connection from ('172.17.0.2', 41628)
Server: recv CREATE TABLE BOOKS(isbn char(14), title char(80), price decimal);

Server: send Success
```

```
Server: Connection from ('172.17.0.2', 41598)
Server: recv CREATE TABLE BOOKS(isbn char(14), title char(80), price decimal);

Server: send Failure
```

### parallel loader setup and test
Before we can start using the loadCSV.py we need to create the csvfile.

## Sample csvfile used for parallel loader
```
BOOKS
(isbn, title, price)
1232,"""Ender's Shadow""",7.99
1210,"""Dune""",7.99
1234,"""Ender's Game""",7.99
1235,"""Speaker for the Dead""",7.99
1236,"""Xenocide""",7.99
1237,"""Children of the Mind""",7.99
```
The first line must be the name of the table for the database. The second line is the list of values you are referencing in your queries. Be sure that the order for each csv line matches the values. 

## Running tests for loadCSV.py

The loadCSV.py is very similar to the runSQL.py. There are some changes to the commandline arguments, but that is about all. After all the containers have parDBD.py running and our csvfile has been created, we can then execute our loadCSV.py program on our container that is acting as the client. The loadCSV.py program takes two command line arguments: the clusterconfig file, and the csvfile file. An example on how to run the program is shown below

```
python3 loadCSV.py clusterconfig.ini csvfile.csv
```
## Example Output and Error Conditions for loadCSV.py
```
172.17.0.3:50001/mydb1: 4 rows inserted.
172.17.0.4:50001/mydb2: 2 rows inserted.
172.17.0.2:50001/mycatdb: catalog updated.
```

## Version

This is the second version of this project. The runSQL.py file is capable of handling most SQL queries. The loadCSV.py file is capable of parsing csvfiles and inserting tuples into the database tables. Each program will always update the catalog database when appropriate. 

## Authors

* **Brandon Doan**

## Acknowledgments

* NOS Energy Drinks (The real MVP)
