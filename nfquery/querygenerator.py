#!/usr/local/bin/python

import simplejson as json
import logging
import multiprocessing
import sys
import os.path
import hashlib
import MySQLdb
import subprocess
import time

# nfquery imports
from query import query
from subscription import subscription
from db import db
from defaults import defaults
from logger import createLogger
from utils import query_yes_no
from models import Plugin, PrefixList, Source, Parser, List


    # --------------------------- JSON TEST -----------------------------------#
    #q=Query(1, "amada", "FAKE-AV", "27.03.1990", ip="193.140.94.94").__dict__ #
    #queryfile = open('outputs/test.jason', mode='w')                          #
    #queryfile.writelines(simplejson.dumps(q, indent=4)+"\n")                  #
    #queryfile.write(simplejson.dumps(q, indent=4))                            #
    #queryfile.write(simplejson.dumps(q, indent=4))                            #
    #queryfile.close()                                                         #
    #                                                                          #
    #anotherfile=open('test.jason', mode='r')                                  #
    #                                                                          #
    #loaded = simplejson.load(anotherfile)                                     #
    #print loaded                                                              #
    # --------------------------- JSON TEST -----------------------------------#
    
__all__ = ['QueryGenerator']

class QueryGenerator:
    def __init__(self, store, sources=None, plugins=None):
        self.store = store
        self.sources = sources
        self.plugins = plugins
        self.qglogger = createLogger('QueryGenerator', defaults.loglevel)
         

    def run(self):
        self.checkParsers()
        self.executeParsers()
        self.subscription = subscription()
        self.createSubscriptions()


    def reconfigurePlugins(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Reconfiguring plugins')

        #    plugins : {
        #    organization    : 'ULAKBIM'
        #    adm_name        : 'Serdar Yigit'
        #    adm_mail        : 'serdar@ulakbim.gov.tr'
        #    adm_tel         : '312-2989394'
        #    adm_publickey   : '/usr/local/etc/nfquery/plugins/ulakbim_public.key'
        #    prefix_list     : '193.140.94.0/24'
        #    plugin_ip       : '193.140.94.200'
        #    }

        from models import Plugin, PrefixList, Source, Parser, List
       
        plgin = self.store.find(Plugin, Plugin.plugin_id == 10)
        if plgin.one():
            for p in plgin:
                print dir(p)
        sys.exit()

        for i in range(len(self.plugins)):
            plugin = Plugin()
            prefix_list = PrefixList()
            prefix_list.prefix   = unicode(self.plugins[i].prefix_list)
            self.store.add(prefix_list)
            self.store.flush()
            plugin.organization = unicode(self.plugins[i].organization)
            plugin.adm_name = unicode(self.plugins[i].adm_name)
            plugin.adm_mail = unicode(self.plugins[i].adm_mail)
            plugin.adm_tel = unicode(self.plugins[i].adm_tel)
            plugin.adm_publickey_file = unicode(self.plugins[i].adm_publickey_file)
            plugin.plugin_ip = unicode(self.plugins[i].plugin_ip)
            plugin.prefix_id = prefix_list.prefix_id
            self.store.add(plugin)
            self.store.flush()
            self.qglogger.debug(plugin.plugin_id)
            self.qglogger.debug(prefix_list.prefix_id)
        self.store.commit()

    #def reconfigureSources3(self):
    #    from models import Plugin, PrefixList, Source, Parser, List
    #    for index in range(len(self.sources)):
    #        lists = self.store.find(List.list_id, List.list_type == unicode(self.sources[index].listtype))
    #        #list_id = self.store.find(List.list_id, List.list_type == unicode(self.sources[index].listtype)).one()
    #        for i in lists:
    #            print i
    #    sys.exit()

    def reconfigureSources(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Reconfiguring sources')

        dbsources = self.store.find(Source)
        
        # Maintain the table for delete operations
        if dbsources.count > 0:
            sources_list = []
            for index in range(len(self.sources)):
                sources_list.append(self.sources[index].sourcename)
            for source in dbsources:
                if not source.source_name in(sources_list):
                    flag = query_yes_no('Do you approve delete operation', default="no")
                    if flag is True:
                        source_name = source.source_name
                        self.store.find(Source, Source.source_name == '%s' % source.source_name).remove()
                        self.store.find(List, List.list_id == source.list_id).remove()
                        self.store.find(Parser, Parser.parser_id == source.parser_id).remove()
                        self.store.commit()
                        self.qglogger.info('Source %s is deleted' % source_name)
                    else:
                        self.qglogger.info('Not deleted anything.')
                        
        for index in range(len(self.sources)):
            # Check the list type
            list_id = self.store.find(List.list_id, List.list_type == unicode(self.sources[index].listtype)).one()
            print list_id
            print unicode(self.sources[index].listtype)
            if list_id is None:
                self.qglogger.warning('List type couldn\'t be found in the database, please check your configuration.')
                self.qglogger.warning('Assigning default list type value.')
                #list_id = 1
            # Calculate the checksum
            conf_checksum = hashlib.md5()   
            conf_checksum.update(self.sources[index].sourcename + str(self.sources[index].listtype) + 
                                 self.sources[index].sourcelink + self.sources[index].sourcefile    +
                                 self.sources[index].parser     + str(self.sources[index].time_interval) )
            dbchecksum = self.store.find(Source.source_checksum, Source.source_name=='%s' % unicode(self.sources[index].sourcename)).one()
            if dbchecksum is None:
                # Adding new source
                self.qglogger.info('Adding new source %s' % self.sources[index].sourcename)
                try:
                    # Add new parser
                    parser = Parser()
                    parser.parser_script = unicode(self.sources[index].parser)
                    parser.time_interval = self.sources[index].time_interval 
                    self.store.add(parser)
                    self.store.flush()
                    # Add new source
                    source = Source()
                    source.source_name = unicode(self.sources[index].sourcename)
                    source.source_link = unicode(self.sources[index].sourcelink)
                    source.list_id = list_id
                    source.parser_id = parser.parser_id 
                    source.source_checksum = unicode(str(conf_checksum.hexdigest()))
                    self.store.add(source)
                    # Commit changes
                    self.store.commit()
                    self.qglogger.info('New Source added successfully : "%s"' % self.sources[index].sourcename)
                except Exception, e:
                    self.qglogger.error("Error %s" % e)
                    sys.exit()
            elif str(conf_checksum.hexdigest()) != str(dbchecksum):
                # Update source information
                self.qglogger.info('Updating the source %s' % self.sources[index].sourcename)
                try:
                    # Update existing source
                    source = self.store.find(Source, Source.source_name == '%s' % unicode(self.sources[index].sourcename) ).one()
                    source.source_link = unicode(self.sources[index].sourcelink)
                    source.list_id = list_id
                    source.source_checksum = unicode(conf_checksum.hexdigest())
                    self.store.add(source)
                    # Update existing parser
                    parser = self.store.find(Parser,Parser.parser_id == source.parser_id).one()
                    parser.parser_script = unicode(self.sources[index].parser)
                    parser.time_interval = self.sources[index].time_interval
                    self.store.add(parser)
                    # Commit changes
                    self.store.commit()
                    self.qglogger.info('Source updated successfully : "%s"' % self.sources[index].sourcename)
                except Exception, e:
                    self.qglogger.error("Error  %s" % (e.args[0]))
                    sys.exit()
            elif str(conf_checksum.hexdigest()) == str(dbchecksum):
                self.qglogger.info('No need to reconfigure the source : %s' % self.sources[index].sourcename)
            else:
                self.qglogger.error('CHECK CODE')
                print 'conf checksum ' + conf_checksum.hexdigest()
                print 'dbchecksum ' + dbchecksum
                sys.exit()
        # reconfigure subscription types 
        #subs = subscription()
        #subs.createSubscriptionTypes()
        #sys.exit() 

 
    def reconfigureSources_old(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Reconfiguring sources')
        # Delete old sources
        try:
            statement = 'SELECT source_name,parser_id FROM source'
            self.cursor.execute(statement)
            registered_sources = self.cursor.fetchall()
        except Exception, e:
            self.connection.rollback()
            self.qglogger.info('Reconfiguration is not completed')
            self.qglogger.error("Error  %s" % (e.args[0]))
            sys.exit()

        # If we have something in the database
        if registered_sources is not None:
            # Convert the sources dictionary in configuration file to sources list
            sources_list = []
            for i in range(len(self.sources)):
                sources_list.append(self.sources[index].sourcename)
            # Check if db records exists in source list of configuration file
            for source in registered_sources:
                if not(source[0] in(sources_list)):
                    statement1 = 'DELETE FROM source WHERE source_name="%s"' % source[0]
                    statement2 = 'DELETE FROM parser WHERE parser_id=%d' % source[1]
                    try:
                        self.cursor.execute(statement1)
                        self.cursor.execute(statement2)
                        self.qglogger.info('Source is deleted : %s' % source[0])
                    except Exception, e:
                        self.connection.rollback()
                        self.qglogger.info('Reconfiguration is not completed')
                        self.qglogger.error("Error  %s" % (e.args[0]))
                        sys.exit()
    
        for i in range(len(self.sources)):
            # Calculate the checksum
            conf_checksum = hashlib.md5()   
            # However the parser_name column belongs to the parser table, we'll use it in calculation of the checksum of the source,
            # and the checksum will be stored in source table.
            conf_checksum.update( self.sources[index].sourcename     + 
                                  str(self.sources[index].listtype)  + 
                                  self.sources[index].sourcelink     + 
                                  self.sources[index].sourcefile     +
                                  self.sources[index].parser          +
                                  str(self.sources[index].time_interval)
            )
            statement = 'SELECT source_checksum FROM source WHERE source_name="%s"' % (self.sources[index].sourcename)
            self.cursor.execute(statement)
            dbchecksum = self.cursor.fetchone()
            if not dbchecksum:
                # If can't find a checksum, add this new source
                self.qglogger.info('Adding new source %s' % self.sources[index].sourcename)
                try:
                    statement = 'INSERT INTO parser (parser_script, time_interval) VALUES("%s", %d)' % (self.sources[index].parser, self.sources[index].time_interval)
                    self.cursor.execute(statement)
                    parser_id = self.cursor.lastrowid
                    statement = 'SELECT list_id FROM list WHERE list_type="%s"' % (self.sources[index].listtype)
                    self.cursor.execute(statement)
                    list_id = self.cursor.fetchone()
                    if list_id is None:
                        self.qglogger.error('List type can not be found in the database, please check your configuration.')
                        self.qglogger.error('Passing to source entry for reconfiguraiton')
                        continue
                    statement = 'INSERT INTO source (source_name, source_link, list_id, parser_id, source_checksum) VALUES("%s", \'%s\', %d, %d, "%s")' % (
                                self.sources[index].sourcename, self.sources[index].sourcelink, list_id[0], parser_id, conf_checksum.hexdigest() )
                    self.cursor.execute(statement)
                    self.qglogger.info('New Source added successfully : "%s"' % self.sources[index].sourcename)
                except Exception, e:
                    self.connection.rollback()
                    self.qglogger.error("Error %s" % e)
                    sys.exit()
            elif str(conf_checksum.hexdigest()) != str(dbchecksum[0]):
                # Update the source information
                self.qglogger.info('Updating the source %s' % self.sources[index].sourcename)
                try:
                    statement = 'SELECT list_id FROM list WHERE list_type="%s"' % (self.sources[index].listtype)
                    self.cursor.execute(statement)
                    list_id = self.cursor.fetchone()
                    if list_id is None:
                        self.qglogger.error('List type can not be found in the database, please check your configuration.')
                        self.qglogger.error('Passing to source entry for reconfiguraiton')
                        continue
                    # Update source table
                    statement = 'UPDATE source SET source_link="%s", list_id=%d, source_checksum="%s" WHERE source_name="%s" ' % (
                                self.sources[index].sourcelink, self.sources[index].listtype, conf_checksum.hexdigest(), self.sources[index].sourcename
                                )
                    self.cursor.execute(statement)
                    # Update parser table
                    statement = 'UPDATE parser SET parser_script="%s", time_interval=%d WHERE parser_id=(SELECT parser_id FROM source WHERE source_name="%s")' % (
                                 self.sources[index].parser, self.sources[index].time_interval, self.sources[index].sourcename )
                    self.cursor.execute(statement)
                    self.qglogger.info('Source updated successfully : "%s"' % self.sources[index].sourcename)
                except Exception, e:
                    self.connection.rollback()
                    self.qglogger.error("Error  %s" % (e.args[0]))
                    sys.exit()
            elif str(conf_checksum.hexdigest()) == str(dbchecksum[0]):
                self.qglogger.info('No need to reconfigure source :  %s' % self.sources[index].sourcename)
            else:
                self.qglogger.info('CHECK CODE')
                print 'conf checksum ' + conf_checksum.hexdigest()
                print 'dbchecksum ' + dbchecksum
                sys.exit()
        # reconfigure subscription types 
        subs = subscription()
        subs.createSubscriptionTypes()
        #close the cursor and give the database connection.
        self.cursor.close()
        db.sync_database_connection()


    def checkParsers(self):
        '''
            Check if the parser exists in the given path.
        '''
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        for index in range(len(self.sources)):
            if os.path.exists(self.sources[index].parser):
                self.qglogger.info('Parser "%s" Exists, OK!' % self.sources[index].parser)
            else:
                self.qglogger.warning('Parser %s doesn\'t exist\nPlease check the nfquery.conf file' % self.sources[index].parser)

    
    def executeParsers(self, parser=None):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parser is None:
            self.qglogger.debug('running all parsers')
            for index in range(len(self.sources)):
                try:
                    print 'parser = %s ' % self.sources[index].parser
                    returncode = subprocess.call(['python', self.sources[index].parser])
                    if returncode == 0:
                        self.createQuery(self.sources[index].parser)
                    else:
                        self.qglogger.warning('Parser returned with error')
                except Exception, e:
                    self.qglogger.error('got exception: %r, exiting' % (e))
                    continue
                    #sys.exit() ??
        else:
            self.qglogger.debug('running parser %s' % parser)
            for index in range(len(self.sources)):
                if self.sources[index].parser == parser:
                    try:
                        returncode = subprocess.call(['python', self.sources[index].parser])
                        if returncode == 0:
                            self.createQuery(self.sources[index].parser)
                        else:
                            self.qglogger.warning('Parser returned with error')
                    except Exception, e:
                        self.qglogger.error('got exception: %r, exiting' % (e))
                        continue
                        #sys.exit() ??


    def createQuery(self, parsername=None):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        if parsername is None:
            for index in range(len(self.sources)):
                try:
                    outputfile = open(self.sources[index].outputfile, 'r')
                    data = json.load(outputfile)
                    #print data['source_name'], data['update_time'], data['ip_list']
                    outputfile.close()
                except Exception, e:
                    self.qglogger.warning('got exception: %r' % (e))
                    self.qglogger.warning('could not load output of parser %s' % self.sources[index].parser)
                    continue
                # Check values with db and conf file.
                # source_name, listtype, output and update time check should be done here!!!!
                myquery = query(data['source_name'], data['output_type'], data['ip_list'], data['update_time'])
                result = myquery.insert_query()
        else:
            for index in range(len(self.sources)):
                if parsername == self.sources[index].parser:
                    try:
                        outputfile = open(self.sources[index].outputfile, 'r')
                        data = json.load(outputfile)
                        outputfile.close()
                    except Exception, e:
                        self.qglogger.warning('got exception: %r' % (e))
                        self.qglogger.warning('could not create queries for parser %s' % parsername)
                        continue
                    # Check values with db and conf file.
                    # source_name, outputtype, output and update time check should be done here!!!!
                    #if (not (4>output_type>0)):
                    #    self.qlogger.error('output_type must be between 1-3, please look at the definition.\n')
                    myquery = query(data['source_name'], data['output_type'], data['ip_list'], data['update_time'])
                    result = myquery.insert_query()

            
    def createSubscriptions(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        self.qglogger.info('Generating Subscriptions...')
        self.createSourceSubscriptions()
        self.createListSubscriptions()
   

    def createSourceSubscriptions(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        try:
            # Check if source_name is not given, so we work for all sources.
            statement = """SELECT subscription_name FROM subscription WHERE subscription_type=1"""
            self.cursor.execute(statement)
            source_name_list = self.cursor.fetchall()
            if source_name_list is None:
                self.qglogger.error("Source is not registered to database. Run reconfig or check sources.")
                sys.exit()
            self.qglogger.debug(source_name_list)
            for source_name in source_name_list:
                statement = """SELECT query_id FROM query WHERE source_id IN(SELECT source_id FROM source WHERE source_name='%s')""" % source_name[0]
                self.cursor.execute(statement)
                query_id_list = self.cursor.fetchall()
                if query_id_list is None:
                    self.qglogger.debug("We don't have any query for this source.")
                    self.qglogger.error("%s subscription creation is failed." % (source_name) )   # We exit, but may be we can wait for the parser to be executed.
                    sys.exit()
                statement = """SELECT subscription_id FROM subscription WHERE subscription_name='%s'""" % source_name
                self.cursor.execute(statement)
                subscription_id = self.cursor.fetchone()
                statement = """SELECT subs_packet_id FROM subscription_packets WHERE subscription_id=%d""" % subscription_id
                self.cursor.execute(statement)
                subs_packet_id = self.cursor.fetchone()
                if subs_packet_id is None:
                    for qid in query_id_list:
                        ########### eger subs_packet_id varsa burada update yapilacak, yoksa eklenecek 
                        statement = ( """INSERT INTO subscription_packets(subscription_id, query_id)""" + 
                                      """VALUES(%d, %d)""" % (subscription_id[0], qid[0]) )
                        self.cursor.execute(statement)
                        self.qglogger.debug(statement)
                else:
                    statement = ("""SELECT query_id FROM subscription_packets WHERE subscription_id=%d""" % subscription_id[0])
                    self.cursor.execute(statement)
                    query_ids = self.cursor.fetchall()
                    for qid in query_id_list:
                        if not (qid in query_ids):
                            statement = ( """INSERT INTO subscription_packets(subscription_id, query_id)""" +
                                      """VALUES(%d, %d)""" % (subscription_id[0], qid[0]) )
                            self.cursor.execute(statement)
                            self.qglogger.debug(statement)
        except MySQLdb.IntegrityError, message:
            errorcode = message[0] # get MySQL error code
            if errorcode == 1062:
                self.qglogger.debug('Duplicate Entry Warning / No Problem.')
                self.qglogger.info('Duplicate Entry Warning / No Problem.')
            else:
                self.qglogger.error("'Error %s" % (repr(e)))
                sys.exit()
        except Exception, e:
            self.qglogger.error("Error %s" % (repr(e)))
            sys.exit ()
            return 0
        db.sync_database_connection()



    def createListSubscriptions(self):
        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
        try:
            # Check if source_name is not given, so we work for all sources.
            statement = """SELECT subscription_name FROM subscription WHERE subscription_type=2"""
            self.cursor.execute(statement)
            list_type_list = self.cursor.fetchall()
            if list_type_list is None:
                self.qglogger.error("List type is not registered to database. Run reconfig or check sources.")
                sys.exit()
            self.qglogger.debug(list_type_list)
            for list_type in list_type_list:
                statement = """SELECT query_id FROM query WHERE source_id IN (SELECT source_id FROM source where list_id IN(SELECT list_id FROM list WHERE list_type='%s'))""" % list_type[0]
                self.cursor.execute(statement)
                query_id_list = self.cursor.fetchall()
                if query_id_list is None:
                    self.qglogger.debug("We don't have any query for this list type.")
                    self.qglogger.error("%s subscription is failed." % (list_type[0]) ) 
                else:
                    statement = """SELECT subscription_id FROM subscription WHERE subscription_name='%s'""" % list_type[0]
                    self.cursor.execute(statement)
                    subscription_id = self.cursor.fetchone()
                    statement = """SELECT subs_packet_id FROM subscription_packets WHERE subscription_id=%d""" % subscription_id
                    self.cursor.execute(statement)
                    subs_packet_id = self.cursor.fetchone()
                if subs_packet_id is None:
                    for qid in query_id_list:
                        ########### eger subs_packet_id varsa burada update yapilacak, yoksa eklenecek 
                        statement = ( """INSERT INTO subscription_packets(subscription_id, query_id)""" +
                                      """VALUES(%d, %d)""" % (subscription_id[0], qid[0]) )
                        self.cursor.execute(statement)
                        self.qglogger.debug(statement)
                else:
                    statement = ("""SELECT query_id FROM subscription_packets WHERE subscription_id=%d""" % subscription_id[0])
                    self.cursor.execute(statement)
                    query_ids = self.cursor.fetchall()
                    for qid in query_id_list:
                        if not (qid in query_ids):
                            statement = ( """INSERT INTO subscription_packets(subscription_id, query_id)""" +
                                      """VALUES(%d, %d)""" % (subscription_id[0], qid[0]) )
                            self.cursor.execute(statement)
                            self.qglogger.debug(statement)
        except MySQLdb.IntegrityError, message:
            errorcode = message[0] # get MySQL error code
            if errorcode == 1062:
                self.qglogger.debug('Duplicate Entry Warning / No Problem.')
                self.qglogger.info('Duplicate Entry Warning / No Problem.')
            else:
                self.qglogger.error("'Error %s" % (repr(e)))
                sys.exit()
        except Exception, e:
            self.qglogger.error("Error %s" % (repr(e)))
            sys.exit ()
            return 0
        db.sync_database_connection()


#-------------------------------------------------------------------------------------------------------------------------------#

#    def generateSubscriptions(self, subscription_type=None, subscription_name=None):
#        self.qglogger.debug('In %s' % sys._getframe().f_code.co_name)
#        if subscription_type is not None:
#            # means all sources and lists subscriptions
#            try:
#                statement = """ SELECT subscription_id FROM subscription WHERE subscription_type=%d""" % subscription_type
#                
#        elif not(subscription_name is None):
#            # means for a specific subscription
#            try:
#                statement = """ SELECT subscription_id FROM subscription WHERE subscription_type=%d"""
#        try:
#            statement = """SELECT subscription_name FROM subscription WHERE subscription_type=2"""

## place this function in elsewhere
#def create_query(source_name, output_type, output, creation_time):
#    '''
#      Get query information from parser and insert the query to database.
#    '''
#    myquery = query(source_name, output_type, output, creation_time)
#    result = myquery.insert_query()
#    if result>0:
#        sys.exit(1)
#    #myquery.print_content()






