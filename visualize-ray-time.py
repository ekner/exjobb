import sqlite3

# connect to db
dbCon = sqlite3.connect("data.db")
dbCur = dbCon.cursor()

for i in range(0, 19):
    dbEntry = dbCur.execute('SELECT ray_time FROM data WHERE ray_time > ? AND ray_time < ?', [i, i+1])
    res = dbEntry.fetchall()
    print(f"{i} - {i+1}: {len(res)}")
