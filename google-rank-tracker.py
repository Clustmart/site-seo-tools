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
# from pycookiecheat import chrome_cookies
import requests
import smtplib
import configparser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Customize path to your SQLite database
database = "rank.db"



# Creating desktop function with 4 arguments.
def desktop(cursor, now, keyword, sitename, device, useragent):
    parser = 'html.parser'

    url = 'https://www.google.com/search'
    browser = RoboBrowser(history=False, user_agent=useragent, parser=parser)
    browser.open(url + '?num=100&q=' + keyword)

    # TBD: check if the page include a form

    # links = browser.find_all("div", {"class": "KJDcUb"})
    # desktop div where URLs are
    links = browser.find_all("div", {"class": "g"})
    

    counter = 0

    logging.debug("+++ Keyword: " + keyword)
    logging.debug('User agent: ' + useragent)
    logging.debug("links")
    logging.debug(str(links))
    logging.debug("===")
    # check if google resonses with error (e.g. too many accesses)
    if str(links) == "[]":
        # check the page content
        links = browser.find_all("html")
        # open text file
        text_file = open("google_output.html", "w")
        # write string to file
        text_file.write(str(links))
        # close file
        text_file.close()
        # Inform by email
        msg['Subject']="ERROR: program stopped! google-rank-tracker.py | " + str(now) 
        msg.attach(MIMEText("ERROR", 'plain'))
        s.send_message(msg)
        # stop querying google, end programm
        sys.exit(0)

    d = []
    
    for i in links:
        counter = counter + 1
        # Store top 3 urls in the keywords database
        if counter == 1:
            logging.debug("i: "+ str(i))
            url = i.find_all('a', href=True)
            position = "%d" % (counter)
            # logging.debug(url[0])
            try:
                rank = "%s" % (url[0]['href'])
            except:
                rank="-X-"
            update = "UPDATE keywords SET '1url'='"+rank+"' WHERE keyword='"+ keyword+"'"
            execute(cursor, update)
            # print("1URL"+rank)
        if counter == 2:
            logging.debug("i: "+ str(i))
            url = i.find_all('a', href=True)
            position = "%d" % (counter)
            rank = "%s" % (url[0]['href'])
            update = "UPDATE keywords SET '2url'='"+rank+"' WHERE keyword='"+ keyword+"'"
            execute(cursor, update)
            # print("2URL"+rank)
        if counter == 3:
            logging.debug("i: "+ str(i))
            url = i.find_all('a', href=True)
            position = "%d" % (counter)
            rank = "%s" % (url[0]['href'])
            update = "UPDATE keywords SET '3url'='"+rank+"' WHERE keyword='"+ keyword+"'"
            execute(cursor, update)
            # print("3URL"+rank)
        # find the position in the google search for you url
        if sitename in str(i):
            url = i.find_all('a', href=True)
            position = "%d" % (counter)
            rank = "%s" % (url[0]['href'])
            keyword = keyword
            device = device
            d.append(keyword)
            d.append(position)
            d.append(rank)
            d.append(device)
            d.append(now)
            # print("KEY:" + keyword, "POS:" + position, "RANK:" + rank, device, now)
            insert = "INSERT INTO rankings (url, keyword, date, rank, device) values ('" + rank + "', '" + keyword + "', '" + now[:7] + "', " + position + ", '" + device + "')"
            execute(cursor, insert)
            #cursor.execute(insert)


# execute query
def execute(c, query):
    logging.debug("SQL:"+query)
    try:       
        c.execute(query)
        c.execute("COMMIT")
    except Exception as err:
        print('Query Failed: %s\nError: %s' % (query, str(err)))

# check if 3url is filled out - if so, skip yhe keyword, as we do not want to check this one so often
def empty3url(c, keyword):
    query='select "3url" from keywords where keyword="' + keyword +'"'
    try:
        c.execute(query)
    except Exception as err:
        print('Query Failed: %s\nError: %s' % (query, str(err)))
    row=c.fetchone()
    return not row[0]

def main():
    # activate logging
    logging.basicConfig(filename='rank_db.log', level=logging.ERROR, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S ')

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

    # Terminal arguments to pass when running the script
    # if no arguments, display syntay
    argn = len(sys.argv)
    # print(argn)
    if argn < 2:
        print("Program call: python https://website.com [device]")
        print("device may be: desktop / mobile")
        # print("an optional project name can be provided. It will be stored in the rankings table")
        sys.exit(0)
    else:
        sitename = sys.argv[1]
        if argn == 2:
            # set desktop as default browsing device
            device = "desktop"
        else:
            device = sys.argv[2]
    logging.info("=======================")
    logging.info("Program start with URL "+ sitename + ", device " + device) 
    external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    logging.debug("External IP: " + external_ip)
    logging.info("=======================")
    # Connect to the database
    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
    except Exception as err:
        print('Connecting to DB failed due to: %s\nError: %s' % (str(err)))


    # now = datetime.date.today().strftime("%d-%m-%Y")
    now = datetime.date.today().strftime("%Y-%m-%d")

    re = cursor.execute("select count(*) from keywords where last_visited = '' or last_visited is NULL or last_visited <> '" + str(now[:7]) +"'")
    result = re.fetchone()
    remaining = result[0]

    re = cursor.execute("SELECT keyword, last_visited FROM keywords ORDER by monthly_searches DESC")
    item = 0

    # send an email at program start
    msg = MIMEMultipart()       # create a message

    # setup the parameters of the message
    msg['From']=config['Email']['Email']
    msg['To']=config['Email']['Email_To']
    msg['Subject']="STARTED google-rank-tracker.py | ↓" + str(remaining) + " | " +str(now) 

    # add in the message body
    msg.attach(MIMEText("OK", 'plain'))

    # send the message via the server set up earlier.
    s.send_message(msg)

    # del msg

    keywords = re.fetchall()
    for keyword in keywords:
        item = item + 1

        kw = keyword[1]
        if kw == None:
            kw = "xxxxxxx"
        if kw[:7] != now[:7]:
            # print("↓"+str(remaining) + " -- " + str(item) + " / " + keyword[0])
            logging.info("↓"+str(remaining) + " -- " + str(item) + " / " + keyword[0])
            remaining = remaining - 1

            if device == 'desktop':
                useragent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
                desktop(cursor, now, keyword[0], sitename, device, useragent)

            # remember when keyword was last verified
            try:
                update = "UPDATE keywords SET last_visited='" + now[:7] + "' WHERE keyword='" + keyword[0] + "'"
                #print(update)
                execute(cursor, update)
            except Exception as err:
                print('DB update failed %s\nError: %s' % (update, str(err)))
            # wait a little
            t = randint(88, 149)
            # print('Sleeping time is', t, 'Seconds')
            time.sleep(t)
            # input("Press Enter to continue...")
 #           else:
 #               print("not empty")

 #       else:
 #           print(keyword[0]+ " - already visited today")


    cursor.close()
    msg['Subject']="ENDED google-rank-tracker.py | ✓" + str(now) 
    # add in the message body
    msg.attach(MIMEText("OK", 'plain'))
    s.send_message(msg)

if __name__ == '__main__':
    main()
