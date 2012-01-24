#!/usr/local/bin/python

import datetime
import os
import sys 

# importable functions 
__all__ = ['fetch_source', 'parse_source']

def fetch_source(source_link, source_file):
    os.system("fetch -o " + source_file + " " + source_link)

def parse_source_and_create_output(source_name, source_file, output_file):
    '''
        Malc0de Parser
    ''' 
    
    # list_types = Botnet, Malware, Spam, Phishing, Virus
    # THINK ! #list_type = 1

    update_time = datetime.datetime.now()
    update_time = update_time.strftime("%Y-%m-%d %H:%M")
    
    ip_list = ''

    try:
        source = open(source_file,"r")
        output = open(output_file, "w")
    except Exception, e:
        print 'Exception'

    output.write('sourcename : %s\n' % source_name)
    output.write('update_time : %s\n' % update_time)
    
    # parse the file line by line and create an ip list
    for line in source.readlines()[4:]:
        ip_list += line.split("\n")[0] + ' '

    output.write('ip_list : %s\n' % ip_list)

    output.close()
    source.close()


if __name__ == "__main__":
    print 'calling main'

    # making parameter assignments manually for now.

    source_name = 'Malc0de'
    source_link = 'http://malc0de.com/bl/IP_Blacklist.txt'
    source_file = '/usr/local/nfquery/sources/malc0de/malc0deSourceFile.txt'
    output_file = '/usr/local/nfquery/sources/malc0de/malc0deOutputFile.txt'

    fetch_source(source_link, source_file)
    parse_source_and_create_output(source_name, source_file, output_file)
    
    
    
    
