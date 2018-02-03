import sys
import sqlite3
import socket
import configparser
import threading
import queue

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
fd = open(sys.argv[2])                      #opens file from second argument in command line, should be the ddlfile with query
query = fd.read()                           #saves the query so file can be closed
fd.close()
tables = []                                 #array that will store all the tables listed in the query
parse = query.split(" ")                    #array that does a split of the query for rudimentary parsing later on

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
        data = mySocket.recv(1024).decode() #saves the success or failure message sent from server
        print (hostname + " " + sys.argv[2] + " " + str(data))  #prints out the server hostname where query was sent as well as ddlfile that the query came from and the success or failure message
        mySocket.close()                    #closes socket object
        data_str = str(data)                #converts data to a string
#if statement that is used to check the success/fail message, places a 1 in queue for success and 0 for failure
        if data_str == "Success":
            queue.put(1)
        else:
            queue.put(0)

#function for creating the catalog table in the catalog database
#parameters: cursor: sqlite cursor that executes ddl commands to database
#connection: connection to catalog database
def create_catalog(cursor, connection):
#DDL statement that creates the catalog table
        createStatement = """CREATE TABLE DTABLES(tname char(32),
        nodeurl char(128), 
        partmtd int, 
        nodeid int, 
        partcol char(32), 
        partparam1 char(32),
        partparam2 char(32));"""
        cursor.execute(createStatement)     #executes the query to the database
        connection.commit()                 #saves the changes made to the database

#function for removing all the corresponding rows from the catalog table when a drop statement occurs in the ddlfile
#parameters: cursor: sqlite cursor that executes ddl commands to database
#tname: name of the table that was dropped, used to delete all rows for every database that stored the table
#connection: connection to catalog database
def remove_catalog(cursor, tname, connection):
        dropStatement = """DELETE FROM DTABLES WHERE tname = {tn}; """  
        cursor.execute(dropStatement.format(tn=tname))   #executes the query to the database
        connection.commit()                 #saves the changes made to the database

#function for adding a row to the catalog table when a create statement occurs in the ddlfile
#parameters: cursor: sqlite cursor that executes ddl commands to database
#tname: name of the table that was dropped, used to delete all rows for every database that stored the table
#nodeurl: hostname for server that table is stored at
#partmtd: partition method used
#nodeid: node number for the database stored at
#partcol: is the column(s) used by the partition method to partition the data in the table
#partparam1: parameters associated with the particular partition method
#partparam2: parameters associated with the particular partition method
#connection: connection to catalog database
def add_catalog(cursor, tname, nodeurl, partmtd, nodeid, partcol, partparam1, partparam2, connection):
        insertStatement = """INSERT INTO DTABLES VALUES ("{tn}", "{nurl}", {pmtd}, {nid}, "{pcol}", "{pp1}", "{pp2}");"""
        cursor.execute(insertStatement.format(tn=tname, nurl=nodeurl, pmtd=partmtd, nid=nodeid, pcol=partcol, pp1=partparam1, pp2=partparam2))    #executes the query to the database
        connection.commit()                 #saves the changes made to the database

'''
Main function is a client that sends queries to multiple databases on a network for execution
this function also creates a catalog database if one does not already exist, as well as updating the
catalog when queries that contain create or drop statements are successfully executed. 
the function takes two command line arguments, the first is the config file that contains the information on all the databases within the network, the second is the ddlfile that contains the query to be executed.
'''
def Main():
#try statement for creating the catalog database table if it does not exist, otherwise saves a boolean value that the catalog was already created
        try:
            create_catalog(cursor, connection)
        except:
            cat_created = False
        success = []                        #array that will be used to hold the queue values for successful queries
        updated = 0                         #boolean value that is used to show if catalog was updated
        count = 0                           #integer to hold the amount of times we iterate through the for loop that updates the catalog database
        tables = []                         #array to hold the tables used in the query
        firstsplit = []                     #array to help in the rudimentary parsing of the query
        nodeid = []                         #array to hold the nodeid where query was sent
        hostnames = []                      #array to hold the hostname where query was sent
        parse = query.split(" ")            #rudimentary parse of the query
#for loop the parses the query, finds every instance of table and stores the tablename into the table array variable
        for x, word in enumerate(parse):    
            if word == "TABLE":
                firstsplit.append(parse[x + 1])
#for loop that completes the second part of the parse
        for x in firstsplit:
            split = x.split('(', 1)
            tables.append(split[0])
        nodes = ConfigSectionMap("nodecount")['numnodes']  #variable to hold the total amount of nodes listed in the catalog databse
        threads = []                        #array to hold the parallel threads that will be created
#for loop that creates the threads to send queries to multiple servers, and then saves them to the threads array.
        for x in range(1, int(nodes) + 1):
            section = "node " + str(x)
            threads.append(myThread(x, ConfigSectionMap(section)['hostname'], ConfigSectionMap(section)['ip'], query, queue))
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
                if parse[0] == "DROP":
                    remove_catalog(cursor, tables[0],connection)
                    updated = 1
                if parse[0] == "CREATE":
                    add_catalog(cursor, tables[0], hostnames[count], 0, nodeid[count], 0, 0, 0, connection)
                    updated = 1
            count += 1 
#for loop checks to see if any of the queries succeeded and contained a drop or create statement, if true, prints out a catalog updated statement, and if false, prints out catalog had no updates
        if updated == 1:
            print(cathost + ": catalog updated.")
        else:
            print(cathost + ": catalog had no updates.")
        connection.close()                  #closes the connection to the database
        
if __name__ == '__main__':
    Main()
