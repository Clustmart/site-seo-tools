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
import logging
import urllib.request
from urllib.parse import urlparse
import smtplib
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

parser = 'html.parser'

# check if url already was recorded in competition table
def unknown_competition(curs, url):
    unknown = True
    query ="select count(url) from competition where url='" + url + "'"
    logging.debug(query)
    curs.execute(query)
    result=curs.fetchone()
    rc=result[0]
    if rc > 0:
        unknown = False
    logging.debug(unknown)
    return unknown

def get_alexa_rank(url, keywords, metrics):
    rank_alexa = 0

    useragent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"
    cookies = {"CONSENT": "YES+cb.20211212-16-p1.ro+FX+724"}

    browser = RoboBrowser(history=False, user_agent=useragent, parser=parser)
    browser.session.cookies.update(cookies)
    browser.open('https://www.alexa.com/siteinfo/'+url)

    rankmini = browser.find_all("div", {"class": "rankmini-rank"})
    # print(rankmini)
    try:
        rankmini_txt = rankmini[0]
    except:
        rank_alexa = -1
    # remove <span> tag and content

    if rank_alexa > -1:
        rankmini_txt = re.sub('<span>.*?</span>', '', str(rankmini_txt))
        
        s = rankmini_txt.split()
        rank_alexa = s[2]

        kw = browser.find_all("div", {"class": "keyword"})
        mtr = browser.find_all("div", {"class": "metric_one"})
        cleanstr = re.compile('<.*?>')

        index = 0
        for record in kw:
            if index > 0 and index < 6:
                keyword = re.sub(cleanstr, '', str(kw[index]))
                keyword = keyword.strip()

                metric = re.sub(cleanstr, '', str(mtr[index]))
                metric = metric.strip()
                keywords[index] = keyword
                metrics[index] = metric
            index = index +1


        logging.debug("Alexa:"+rank_alexa)
        rank_alexa = rank_alexa.replace(',', '')
        logging.debug("Alexa:"+rank_alexa)
        t = randint(30,80)
        # print('Sleeping time is' ,t ,'Seconds')
        time.sleep(t)
    return rank_alexa


def insert_competition(url, curs, now):
    url = urlparse(url)
    domain = url.hostname
    if domain != None:
        logging.debug("Domain:"+domain)

        if unknown_competition(curs, domain):
            keywords = ["", "", "", "", "", ""]
            metrics = [0, 0, 0, 0, 0, 0]
            alexa = get_alexa_rank(domain, keywords, metrics)
            insert = "'" + domain + "', '" + str(alexa) + "', '" + now[-7:] + "', '" + keywords[1] + "', '" + str(metrics[1]) + "', '" + keywords[2] + "', '" + str(metrics[2]) + "', '" + keywords[3] + "', '" + str(metrics[3]) + "', '" + keywords[4] + "', '" + str(metrics[4]) + "', '" + keywords[5] + "', '" + str(metrics[5]) + "'"
            logging.debug("I1:" + insert)
            insert = "INSERT INTO competition (url, alexa, date, k1, p1, k2, p2, k3, p3, k4, p4, k5, p5) VALUES (" + insert + ")"            
            logging.debug("I2:" + insert)
            try:
                curs.execute(insert)
                curs.execute("COMMIT")
            except Exception as err:
                print('Inserting to DB failed due to: %s' % (str(err)))



def main():
    # activate logging
    logging.basicConfig(filename='competition.log', level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S ')

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

    # Read initialization parameters
    config = configparser.ConfigParser()
    try:
        config.read("site-seo-tools.ini")
    except Exception as err:
        print('Cannot read INI file due to Error: %s' % (str(err)))
    s = smtplib.SMTP_SSL(host=config['Email']['Host'], port=config['Email']['Port'])
    #s.starttls()
    s.ehlo()
    s.login(config['Email']['Email'], config['Email']['Password'])

    now = datetime.date.today().strftime("%d-%m-%Y")

    query = "SELECT * FROM keywords where last_visited ='" + now[-7:]+ "' ORDER BY monthly_searches DESC"
    logging.debug(query)
    re = cursor.execute(query)
    cols = re.fetchall()

    for col in cols: 
        insert_competition(col[3], cursor, now)
        insert_competition(col[4], cursor, now)
        insert_competition(col[5], cursor, now)

    cursor.close()
    # Send email when run ended
    # setup the parameters of the message
    msg = MIMEMultipart()       # create a message
    msg['From']=config['Email']['Email']
    msg['To']=config['Email']['Email_To']
    msg['Subject']="ENDED alexa_site_rank.py | ↓" + str(now) 

    # add in the message body
    msg.attach(MIMEText("OK", 'plain'))

    # send the message via the server set up earlier.
    s.send_message(msg)

if __name__ == '__main__':
    main()
