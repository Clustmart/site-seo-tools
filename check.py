import sqlite3
import datetime
import time

database = "rank.db"

# Connect to the database
try:
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
except Exception as err:
    print('Connecting to DB failed due to: %s\nError: %s' % (str(err)))

now = datetime.date.today().strftime("%Y-%m-%d")

# re = cursor.execute("select count(*) from keywords where last_visited = '' or last_visited is NULL")
re = cursor.execute("select count(*) from keywords where last_visited = '' or last_visited is NULL or last_visited <> '" + str(now[:7]) +"'")
result = re.fetchone()
print(str(result[0]))
