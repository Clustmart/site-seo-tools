import sqlite3

database = "rank.db"

# Connect to the database
try:
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
except Exception as err:
    print('Connecting to DB failed due to: %s\nError: %s' % (str(err)))

re = cursor.execute("select count(*) from keywords where last_visited = '' or last_visited is NULL")
result = re.fetchone()
print(str(result[0]))
