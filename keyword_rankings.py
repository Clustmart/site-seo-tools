import sys
import re
import random
from random import randint
import datetime
import pandas as pd
import time
import sqlite3
import logging




def get_rank(keyword, curs, now):
    query = "SELECT rank from rankings WHERE keyword='" + keyword + "' AND date='" + now + "'"
    logging.debug("get_rank():" + query)
    re = curs.execute(query)
    a_rank = re.fetchone()
    if a_rank is None:
        rank = 0
    else:
        rank = a_rank[0]
    return rank




def main():
    # activate logging
    logging.basicConfig(filename='keyword_rankings.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S ')

    # if needed, change here database path and name
    database = "rank.db"

    logging.info("=======================")
    logging.info("Program started") 

    # Connect to the database
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
    except Exception as err:
        print('Connecting to DB failed due to: %s\nError: %s' % (str(err)))


    now = datetime.date.today().strftime("%Y-%m-%d")

    query = "SELECT keyword FROM keywords where last_visited ='" + now[:7]+ "' ORDER BY monthly_searches DESC"
    logging.debug(query)
    re = cursor.execute(query)
    keywords = re.fetchall()

    for kw in keywords: 
        rank = get_rank(kw[0], cursor, now[:7])
        query = "UPDATE keywords SET rank='" + str(rank) + "' where last_visited ='" + now[:7]+ "' AND keyword='" + kw[0] + "'"
        logging.debug(query)
        re = cursor.execute(query)
    query = "COMMIT"
    re = cursor.execute(query)

    cursor.close()

if __name__ == '__main__':
    main()
