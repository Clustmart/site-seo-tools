#####################################################################
# Curated Content
# Checks ranking for the curated content and stores it on a
# monthly base in a curated_content_history table
#  - stores in curated_content the minimum for rank (the best)
#  - stores in curated_content_history all occurences for article
#####################################################################
# Version: 0.1.5
# Email: paul.wasicsek@gmail.com
# Status: dev
#####################################################################

from pprint import pprint
from random import randint
import pandas as pd
import sqlite3
import logging as log
import configparser


# global variables
last_visited = ""
article_rank = 0

# Read initialization parameters
config = configparser.ConfigParser()
try:
    config.read("config.ini")
except Exception as err:
    print("Cannot read INI file due to Error: %s" % (str(err)))

# activate logging
log.basicConfig(
    filename="curated_content.log",
    level=log.DEBUG,
    format="%(asctime)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S ",
)

log.info("=======================")
log.info("Program started")

# Customize path to your SQLite database
database = "rank.db"

# Connect to the database
try:
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
except Exception as err:
    print("Connecting to DB failed due to: %s\n" % (str(err)))

# execute query
def execute(query, param=""):
    log.debug("SQL:" + query)
    if len(param) > 0:
        log.debug("Param:" + str(param))
    return_value = ""
    try:
        return_value = cursor.execute(query, param)
        if query.startswith("UPDATE") or query.startswith("INSERT"):
            cursor.execute("COMMIT")
    except Exception as err:
        print("Query Failed: %s\nError: %s" % (query, str(err)))
    return return_value


# get_rank
# query table rangings for the article_id and return
#   rank
#   keyword
#   date
def get_rank(article):
    query = (
        "SELECT rank, keyword, date from rankings WHERE url LIKE '%"
        + str(article[0])
        + "%'"
    )
    re1 = execute(query)
    re_rank = re1.fetchall()
    if len(re_rank) == 0:
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
        last_visited = ""
        article_rank = 1000
        article_keyword = ""
        if re_rank != 0:
            # pprint(re_rank[0])
            for rank in re_rank:
                query = "INSERT INTO curated_content_history (id_content, rank, link, keyword, date) VALUES (?, ?, ?, ?, ?)"
                param = (article[0], rank[0], "", rank[1], rank[2])
                execute(query, param)
                # if rank[2] >= last_visited:
                #     last_visited = rank[2]
                #     article_rank = rank[0]
                #     article_keyword = rank[1]

                if rank[0] < article_rank:
                    article_rank = rank[0]
                    last_visited = rank[2]
                    article_keyword = rank[1]
                    query = "UPDATE curated_content SET last_visited=?, rank=?, keyword=? WHERE id_content=?"
                    param = (last_visited, article_rank, article_keyword, article[0])
                    execute(query, param)

                # query = "UPDATE curated_content SET last_visited=?, rank=?, keyword=? WHERE id_content=?"
                # param = (last_visited, article_rank, article_keyword, article[0])
                # execute(query, param)

    cursor.close()


if __name__ == "__main__":
    main()
