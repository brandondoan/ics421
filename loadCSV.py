import sys
import sqlite3
import socket
import configparser
import threading
import queue
import time
import csv

connection = sqlite3.connect("mycatdb.db")  #object for connection to sqlite database for this server
cursor = connection.cursor()                #cursor to execute DDL commands to local database
Config = configparser.ConfigParser()        #parser created to parse the clusterconfig.ini file
Config.read(sys.argv[1])                    #open the config file listed in 1st command line arg
queue = queue.Queue()                       #queue used to store either a 1 or 0, as a determiner for if our ddlfile was successfully updated to the target database. 1 = success 0 = fail
#function to use the configparser to parse and map the config file
#parameters: section: is the name of the section in config file that you wish to access.
#after invoking the function, you must type the value you are searching for
def ConfigSectionMap(section):
    dict1 = {}                              #dictionary to store the values of a section
    options = Config.options(section)       #list of values
#adds all the values in a section to the dictionary
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

catip = ConfigSectionMap("catalog")['ip']   #stores the catalog database ip 
cathost = ConfigSectionMap("catalog")['hostname']  #stores the catalog database hostname
numnodes = int(ConfigSectionMap("nodecount")['numnodes'])
nodeurl = []
insertStmt = 'INSERT INTO '
valuesStmt = '\nVALUES\n'
sqlStatement = []
values = []
queries = []
rowlist = []
section = []
param1 = []
param2 = []
csvlist = []
nodeid = []
hostnames = []
rowcount = []

with open(sys.argv[2]) as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    table = next(csvReader)
    values = next(csvReader)
    sqlStatement.append(insertStmt)
    sqlStatement.append(table[0] + " ")
    sqlStatement.append(', '.join(values))
    sqlStatement.append(valuesStmt)
    for x in range(1, numnodes + 1):
        queries.append(sqlStatement)
    for row in csvReader:
        csvlist.append(row)
table = str(table[0])
method = str(ConfigSectionMap(table)['method'])
column = str(ConfigSectionMap(table)['column'])
if (method == 'range'):
    partmtd = 1
elif (method == 'hash'):
    partmtd = 2
else:
    partmtd = 0
for x in range(1, numnodes + 1):
    section.append("node " + str(x))
    nodeurl.append(str(ConfigSectionMap(section[x-1])['hostname']))
    if (partmtd == 1):
        param1.append(int(ConfigSectionMap(section[x-1])['param1']))
        param2.append(int(ConfigSectionMap(section[x-1])['param2']))
    if (partmtd == 2):
        param1.append(int(ConfigSectionMap(table)['param1']))
        param2.append(0)

if (partmtd == 1):
    for row in csvlist:
        for x in range(1, numnodes + 1):
            if (int(row[0]) >= param1[x-1] and int(row[0]) <= param2[x-1]):
                rowlist.append('(' + ', '.join(row) + '),\n')
                queries[x-1] = queries[x-1] + rowlist
                rowlist.clear()
    for x in range(0, 2):
        rowcount.append(len(queries[x])-4)
        queries[x][len(queries[x])-1] = queries[x][len(queries[x])-1][:-2]
        queries[x] = queries[x] + [';']
        queries[x] = ''.join(queries[x])

if (partmtd == 2):
    for row in csvlist:
        x = (int(row[0]) % param1[0])
        rowlist.append('(' + ', '.join(row) + '),\n')
        queries[x] = queries[x] + rowlist
        rowlist.clear()
    for x in range(0, 2):
        rowcount.append(len(queries[x])-4)
        queries[x][len(queries[x])-1] = queries[x][len(queries[x])-1][:-2]
        queries[x] = queries[x] + [';']
        queries[x] = ''.join(queries[x])

#object creation for a thread that sends queries to servers on the network, utilized mainly for parallelization
#parameters: nodeid: id for the database query is being sent to
#hostname: is the hostname of the server that query is being sent to
#ip: is the ip address for the server that query is being sent to
#query: is the DDL to be executed
#queue: is the queue object that will hold a value to show if the query succeeded or failed
class myThread (threading.Thread):
    def __init__(self, nodeid, hostname, ip, query, queue):
        threading.Thread.__init__(self)
        self.nodeid = nodeid
        self.hostname = hostname
        self.ip = ip
        self.query = query
        self.queue = queue
    def run(self):
        run_query(self.nodeid, self.hostname, self.ip, self.query, self.queue)

#function for thread that connects to the server and sends query, records success or failure through the queue
#parameters: nodeid: id for the database query is being sent to
#hostname: is the hostname of the server that query is being sent to
#ip: is the ip address for the server that query is being sent to
#query: is the DDL to be executed
#queue: is the queue object that will hold a value to show if the query succeeded or failed
def run_query(nodeid, hostname, ip, query, queue):
        port = 50001                        #port used for connection to server 
        mySocket = socket.socket()          #creates a socket to allow for network connections
        mySocket.connect((ip,port))         #connects to server where query is being sent
        mySocket.send(query.encode())       #sends the query
        data = mySocket.recv(1024).decode()
        data = data.replace("(", "")
        data = data.replace(")", "\n")
        data = data.replace(",", " ")
        data_str = str(data)                #converts data to a string
#if statement that is used to check the success/fail message, places a 1 in queue for success and 0 for failure
        if data_str == "Failure":
            print (hostname + " " + sys.argv[2] + " " + str(data))  #prints out the server hostname where query was sent as well as ddlfile that the query came from and the success or failure message
            queue.put(0)
        else:
            queue.put(1)
            print (data)
        mySocket.close()

def db_runquery(hostname, ip, query, update):
        port = 50001                        #port used for connection to server
        for x in query:
            mySocket = socket.socket()          #creates a socket to allow for network connections
            mySocket.connect((ip,port))         #connects to server where query is being sent
            mySocket.send(x.encode())       #sends the query
            data = mySocket.recv(1024).decode()
            if (str(data) == "Failure"):
                update.append(0)
            else:
                update.append(1)
            mySocket.close()



'''
Main function is a client that sends queries to multiple databases on a network for execution
this function also creates a catalog database if one does not already exist, as well as updating the
catalog when queries that contain create or drop statements are successfully executed. 
the function takes two command line arguments, the first is the config file that contains the information on all the databases within the network, the second is the ddlfile that contains the query to be executed.
'''
def Main():
#try statement for creating the catalog database table if it does not exist, otherwise saves a boolean value that the catalog was already created
    success = []                        #array that will be used to hold the queue values for successful queries
    updates = []                         #boolean value that is used to show if catalog was updated
    updated = 0
    count = 0                           #integer to hold the amount of times we iterate through the for loop that updates the catalog database
    db_query = []
    for x in range(1, int(numnodes) + 1):
        format_list = []
        format_list.append(table)
        format_list.append(nodeurl[x-1])
        format_list.append(partmtd)
        format_list.append(x)
        format_list.append(column)
        format_list.append(param1[x-1])
        format_list.append(param2[x-1])
        db_query.append("INSERT OR REPLACE INTO DTABLES (tname, nodeurl, partmtd, nodeid, partcol, partparam1, partparam2)\nVALUES\n('{}', '{}', {}, {}, '{}', '{}', '{}');".format(*format_list))
    db_runquery(cathost, catip, db_query, updates)
    threads = []                        #array to hold the parallel threads that will be created
#for loop that creates the threads to send queries to multiple servers, and then saves them to the threads array.
    for x in range(1, int(numnodes) + 1):
        section = "node " + str(x)
        threads.append(myThread(x, ConfigSectionMap(section)['hostname'], ConfigSectionMap(section)['ip'], queries[x-1], queue))
        (threads[-1].start())           #starts all threads
        nodeid.append(x)                #saves the node where the thread is sending the query to into the nodeid array
        hostnames.append(ConfigSectionMap(section)['hostname'])   #saves the hostname where the thread is sending the query to into the hostnames array
#for loop that joins all the threads
    for t in threads:
        t.join()
#while loop to save the success or fail of every thread into the success array
    while not queue.empty():
        success.append(queue.get())
#for loop that iterates through the success array, if a query was successfully updated it checks to see if the query contained a drop or create statement.
#if so, calls the proper function to update the catalog
    for x in success:
        if x == 1:
            print (hostnames[count] + ": " + str(rowcount[count]) + " rows inserted.")
        count += 1 
#for loop checks to see if any of the queries succeeded and contained a drop or create statement, if true, prints out a catalog updated statement, and if false, prints out catalog had no updates
    for x in updates:
        if x == 1:
            updated = 1
    if(updated == 1):     
        print(cathost + ": catalog updated.")
    else:
        print(cathost + ": catalog had no updates.")
    connection.close()                  #closes the connection to the database
    print(updates)
if __name__ == '__main__':
    Main()
