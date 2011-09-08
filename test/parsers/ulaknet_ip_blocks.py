#!/usr/local/bin/python

import MySQLdb
import sys
import re

# Open database connection
db = MySQLdb.connect("localhost","nfquery","nf1!","ulaknet")
# prepare a cursor object using cursor() method
cursor = db.cursor()

# get node information
get_node_information="SELECT id,short_name,long_name FROM Nodes"
Node={}
cursor.execute(get_node_information)
rows=cursor.fetchall()
output=open("outputs/UcBilgileri","w")

head="%-*s%-*s%-*s%*s"
column1_width=15
column2_width=20
column3_width=25
column4_width=20

output.write(head % (column1_width, "ID", column2_width, "Uc_kisa", column3_width ,"Network Bilgisi", column4_width, "MailAddress\n"))

for row in rows:
    Node["id"]=row[0] 
    Node["shortname"]=row[1] 
    Node["longname"]=row[2] 
    get_mail_addresses="SELECT email FROM Responsibles WHERE id=" + str(Node["id"])
    cursor.execute(get_mail_addresses)
    mailaddr=cursor.fetchone()
    try:
        Node["mailaddr"]=mailaddr[0]
    except:
        Node["mailaddr"]="----"
    get_block_id_info="SELECT block_id FROM Nodes_Blocks WHERE node_id=" + str(Node["id"])
    cursor.execute(get_block_id_info)
    blockids=cursor.fetchall()
    try:
        blockids=[map(int,block) for block in blockids if block is not None]
    except:
        continue
    for blockid in re.findall(r'\d+', str(blockids)):
        get_ip_block_info="SELECT * FROM Ip_Blocks WHERE id=" + blockid;
        cursor.execute(get_ip_block_info)
        ips=cursor.fetchall()
        for ip in ips:
            network_count=(ip[4]-ip[3]+1)/256
            if network_count == 256:
                network=ip[1] + "/16"
                output.write(head % (column1_width, Node["id"], column2_width, Node["shortname"], column3_width, network , column4_width, str(Node["mailaddr"])+"\n"))
            else:
                block=ip[1].split(".")
                for i in range(0,network_count):
                    network=block[0] + "." + block[1] + "." + str(int(block[2])+i) + "." + block[3] + "/24"
                    output.write(head % (column1_width, Node["id"], column2_width, Node["shortname"], column3_width, network , column4_width, str(Node["mailaddr"])+"\n"))
output.close()
cursor.close()
db.close()
