#!/usr/bin/python3

import sqlite3
import matplotlib.pyplot as plt

originalData = {}

x = [] # Matches share
y = [] # No miner

# print("x,y")

def getOriginalData():
    dbCon = sqlite3.connect(f"saved-db/0.db")
    dbCur = dbCon.cursor()
    res = dbCur.execute("SELECT AVG(ray_time) as ray_time FROM data WHERE ray_status = 2")
    originalData["rayTime"] = res.fetchone()[0]

def getFromDb(dbFile):
    data = {}

    dbCon = sqlite3.connect(f"{dbFile}.db")
    dbCur = dbCon.cursor()

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE certain > 0")
    data["certain"] = res.fetchone()[0]

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE certain = 0 AND probable > 0")
    data["probable"] = res.fetchone()[0]

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE certain = 0 AND probable = 0 AND unlikely > 0")
    data["unlikely"] = res.fetchone()[0]

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE certain = 0 AND probable = 0 AND unlikely = 0 AND ray_status = 2")
    data["nominer"] = res.fetchone()[0]

    res = dbCur.execute("SELECT AVG(ray_time), AVG(linesAdded), AVG(linesRemoved), AVG(newFileSize), AVG(matches) FROM data WHERE ray_status=2")
    avg = res.fetchone()
    data["raytime"] = avg[0]
    data["linesadded"] = avg[1]
    data["linesremoved"] = avg[2]
    data["newfilesize"] = avg[3]
    data["matches"] = avg[4]

    res = dbCur.execute("SELECT AVG(matches * 1.0 / linesBefore) FROM data WHERE ray_status=2")
    data["avgmatchesshare"] = res.fetchone()[0]

    # Calculate relative differences:

    res = dbCur.execute("SELECT AVG(linesBefore), AVG(oldFileSize) FROM data WHERE ray_status=2")
    avg = res.fetchone()
    linesBefore = avg[0]
    oldFileSize = avg[1]

    data["averagelinesdiff"] = (data["linesadded"] - data["linesremoved"]) / linesBefore * 100
    data["averagesizediff"] = (data["newfilesize"] - oldFileSize) / oldFileSize * 100
    data["averageraytimediff"] = (data["raytime"] - originalData["rayTime"]) / originalData["rayTime"] * 100

    data["avgmatchesshare"] = data["avgmatchesshare"] * 100
    dbCon.close()

    x.append(data["avgmatchesshare"])
    y.append(data["nominer"])

    #print(f"{data['avgmatchesshare']}, {data['nominer']}")

getOriginalData()

'''

getFromDb("d/d1")
getFromDb("d/d2")
getFromDb("d/d3")
getFromDb("d/d4")
getFromDb("o/o1")
getFromDb("o/o2")
getFromDb("o/o3")
getFromDb("s/s1")
getFromDb("s/s2")
getFromDb("s/s3")
getFromDb("s/s4")
getFromDb("s/s5")
#plt.plot(x, y, 'rx')

lst = [
    12,
    13,
    14,
    15,
    23,
    24,
    25,
    34,
    35,
    45,
    123, 
    124,
    125,
    134,
    135,
    145,
    234,
    235,
    245,
    345,
    1234,
    1235,
    1245,
    1345,
    #2345,
    12345
]
x = []
y = []
for i in range(len(lst)):
    s = "s/s" + str(lst[i])
    getFromDb(s)
#plt.plot(x, y, 'rx')

print("")

x = []
y = []
getFromDb("s/s2345")
#plt.plot(x, y, 'ro')

print("")

x = []
y = []
getFromDb("d/d1_3div14")
getFromDb("d/d2_3div14")
getFromDb("d/d3_3div14")
getFromDb("d/d4_3div14")
#lt.plot(x, y, 'bx')

x = []
y = []
getFromDb("o/o1_3div14")
getFromDb("o/o2_3div14")
getFromDb("o/o3_3div14")
#plt.plot(x, y, 'bx')

x = []
y = []
getFromDb("s/s1_1div2")
#plt.plot(x, y, 'bx')
'''

numerators = [0,0.5,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
obfuscations = ["d1", "o1", "s1"]
colors = ["r", "b", "g"]

i = 0
for obf in obfuscations:
    x = []
    y = []
    for num in numerators:
        if num > 6 and obf == "s1":
            continue
        getFromDb(f"db-plot/{obf}/{num}")
    color = colors[i]
    plt.plot(x, y, f'-{color}x')
    i += 1


plt.xlabel("Match ratio (%)")
plt.ylabel("\"None\" category")
plt.axis([0, 15, 0, 223])
plt.legend(labels=["$D_1$", "$O_1$", "$S_1$"])

#plt.show()
plt.savefig(f'matches-plot.pdf')
plt.figure().clear()
