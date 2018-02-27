import socket
import sys
import sqlite3

connection = sqlite3.connect("mycatdb.db") #object for connection to sqlite3 database for this server
cursor = connection.cursor()             #cursor to execute DDL commands to database

'''
Main function is a server that listens for queries from a client, to execute on its database.
upon execution of query, responds with a message of either failuer or success.
takes in two arguments, the hostname as its first and port address as the second
'''
def Main():
    host = sys.argv[1]                   #sets variable host to 1st command line argument
    port = int(sys.argv[2])              #sets variable port to 2nd command line argument
    while True:
        mySocket = socket.socket()           #creates a socket to allow for network connections
        mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mySocket.bind((host,port))           #assigns hostname and port for the computer
        mySocket.listen(1)                   #sets socket to listen continuously for queries
        conn, addr = mySocket.accept()       #saves the new socket object for sending and recieving to conn, and the address of the other end of the connection is saved to addr
        print ("Server: Connection from " + str(addr))  #prints out the address of the connecting client
        data = conn.recv(1024).decode()      #save the query from client to the variable data for later use
        if not data:                         #if there is no data do nothing
            return
        print("Server: recv " + str(data))  #prints out the query when received
#Try statement attempts to execute the query to the local database, if the query fails
#the program continues on but updates the response message to client as "Failure"
        try:
            cursor.execute(data)
        except:
            msg = "Failure"                  #sends the response message of either a failed or successful query
            conn.send(msg.encode())
        tuples = []                          #array that holds the rows relevant to query
        #for statement to populate the tuples variable with the rows relevant to the query
        for row in cursor:
            tuples.append(str(row))
        for tuple in tuples:
            conn.send(tuple.encode())
        connection.commit()                  #saves the changes made to the database
        conn.close()                         #closes the connection to the client
    connection.close()                   #closes the connection to the database
if __name__ == '__main__':
    Main()
