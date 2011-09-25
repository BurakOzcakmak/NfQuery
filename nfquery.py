#!/usr/local/bin/python

from datetime import date
from config import Config
import os
import SocketServer
import argparse
import MySQLdb


# global paths
nfquery = "/usr/local/nfquery/"
sourcepath = nfquery + "sources/amada/"
outputpath = nfquery + "outputs/amada/"


class db:
    '''
        db class deals with the db operations. It gets the database configuration parameters
        and initiates database connection instance. The attributes and functions described 
        below.

         ----------------
        | Attributes     |
         ----------------

        db_host : 

        db_name :

        db_user :    

        db_password : 

         ----------------
        | Functions      |
         ----------------
        
        connect_db : 

        get_connection_instance:

    '''
    def __init__(self, db_host, db_user, db_password, db_name):
        self.db_host = db_host
        self.db_name = db_name
        self.db_user = db_user
        # We should do something for storing the password, It should be encrypted or hashed?
        self.db_password = db_password

    def connect_db(self):
        '''
           Returns a mysql connection cursor object.
        '''
        try:
           self.connection = MySQLdb.connect(self.db_host, self.db_user, self.db_password, self.db_name)
           self.cursor = self.connection.cursor()
        except MySQLdb.Error, e:
           #print "Error %d: %s" % (e.args[0], e.args[1])
           sys.exit ("Error %d: %s" % (e.args[0], e.args[1]))
        return self.cursor

    def close_db(self):
        '''
           Commit changes to database and close the connection.
        '''
        self.connection.commit()
        self.cursor.close()
        self.connection.close()


    #q=Query(1, "amada", "FAKE-AV", "27.03.1990", ip="193.140.94.94").__dict__
    #queryfile = open('outputs/test.jason', mode='w')
    #queryfile.writelines(simplejson.dumps(q, indent=4)+"\n")
    #queryfile.write(simplejson.dumps(q, indent=4))
    #queryfile.write(simplejson.dumps(q, indent=4))
    #queryfile.close()
    #
    #anotherfile=open('test.jason', mode='r')
    
    #loaded = simplejson.load(anotherfile)
    #print loaded




class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print "%s wrote:" % self.client_address[0]
        print self.data
        # just send back the same data, but upper-cased
        self.request.send(self.data.upper())


if __name__ == "__main__":
    # Parse Command Line Arguments
    parser = argparse.ArgumentParser(description="Process arguments")
    parser.add_argument('conf_file', metavar="--conf", type=str, nargs='?', help='nfquery configuration file'  )
    args = parser.parse_args()

    # Parse Configuration File
    # Notice that configuration file is assigned to args object as args.conf_file
    # We pass nfquery.conf file to Config object to parse general configuration 
    # parameters of NfQuery
    nffile=Config(args.conf_file)
    database = db(nffile.DB_HOST, nffile.DB_USER, nffile.DB_PASSWORD, nffile.DB_NAME)
    dbcursor = database.connect_db()
    #dbcursor.execute("show variables like '%VERSION%';")
    #print dbcursor.fetchall()
    database.close_db()
    

#    HOST, PORT = "localhost", 7777
#
#    # Create the server, binding to localhost on port 9999
#    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
#
#    # Activate the server; this will keep running until you
#    # interrupt the program with Ctrl-C
#    server.serve_forever()




