#####################################################################
## Curated Content
## Checks ranking for the curated content and stores it on a
## monthly base in a curated_content_history table
#####################################################################
## Version: 0.1.0
## Email: paul.wasicsek@gmail.com
## Status: dev
#####################################################################

from pprint import pprint
import sys
import re
import random
from random import randint
from robobrowser import RoboBrowser
import datetime
import csv
import pandas as pd
import time
import sqlite3
import logging as log
import urllib.request
import requests
import smtplib
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# global variables
last_visited=""

# Read initialization parameters
config = configparser.ConfigParser()
try:
    config.read("config.ini")
except Exception as err:
    print('Cannot read INI file due to Error: %s' % (str(err)))

# activate logging
log.basicConfig(filename='curated_content.log', level=log.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S ')

log.info("=======================")
log.info("Program started") 

# Customize path to your SQLite database
database = "rank.db"

# Connect to the database
try:
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
except Exception as err:
    print('Connecting to DB failed due to: %s\n' % (str(err)))

# execute query
def execute(query, param=""):
    log.debug("SQL:" + query)
    if (len(param) > 0):
        log.debug("Param:" + str(param))
    return_value = ""
    try:
        return_value = cursor.execute(query, param)
        if (query.startswith("UPDATE") or query.startswith("INSERT")):
            cursor.execute("COMMIT")
    except Exception as err:
        print('Query Failed: %s\nError: %s' % (query, str(err)))
    return (return_value)

def get_rank(article):
    query = "SELECT rank, keyword, date from rankings WHERE url LIKE '%" + str(article[0])+ "%'"
    re1=execute(query)
    re_rank = re1.fetchall()
    if (len(re_rank)==0):
        rank = 0
    else:
        rank = re_rank
    return rank

def main():
    query = "SELECT id_content FROM curated_content"
    re = execute(query)
    articles = re.fetchall()

    for article in articles: 
        re_rank = get_rank(article)
        last_visited=""    
        if (re_rank != 0):
            # pprint(re_rank[0])
            for rank in re_rank:
                query="INSERT INTO curated_content_history (id_content, rank, link, keyword, date) VALUES (?, ?, ?, ?, ?)"
                param=(article[0], rank[0], "",rank[1],rank[2])
                execute(query,param)     
                if (rank[2] > last_visited):
                    last_visited=rank[2]
            query="UPDATE curated_content SET last_visited=? WHERE id_content=?"
            param=(last_visited, article[0])
            execute(query,param)
                   
    cursor.close()


if __name__ == '__main__':
    main()