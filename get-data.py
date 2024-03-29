#!/usr/bin/python3

import sqlite3
import csv
import numpy

originalData = {}

csvfile = open("data.csv", 'w', newline='')
csvWriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
csvWriter.writerow([
    'obfuscation',
    'convstop',
    'raystop',
    'certain',
    'probable',
    'unlikely',
    'nominer',
    'raytime',
    'linesadded',
    'linesremoved',
    'newfilesize',
    'matches',
    'averagelinesdiff',
    'averagesizediff',
    'averageraytimediff',
    'avgmatchesshare',
    'std',
    'pera',
    'perb',
    'perc',
    'perd',
    'pere'
])

def getOriginalData():
    dbCon = sqlite3.connect(f"saved-db/0.db")
    dbCur = dbCon.cursor()
    res = dbCur.execute("SELECT AVG(ray_time) as ray_time FROM data WHERE ray_status = 2")
    originalData["rayTime"] = res.fetchone()[0]


def getFromDb(dbFile):
    data = {}

    dbCon = sqlite3.connect(f"saved-db/{dbFile}.db")
    dbCur = dbCon.cursor()

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE convert_status != 2")
    data["convstop"] = res.fetchone()[0]

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE ray_status != 2")
    data["raystop"] = res.fetchone()[0]

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE certain > 0")
    data["certain"] = res.fetchone()[0]

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE certain = 0 AND probable > 0")
    data["probable"] = res.fetchone()[0]

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE certain = 0 AND probable = 0 AND unlikely > 0")
    data["unlikely"] = res.fetchone()[0]

    res = dbCur.execute("SELECT COUNT(id) as cnt FROM data WHERE certain = 0 AND probable = 0 AND unlikely = 0")
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

    res = dbCur.execute("SELECT matches * 1.0 / linesBefore FROM data WHERE ray_status=2")
    res = res.fetchall()
    res = list(map(lambda x : x[0] * 100, res))
    data["std"]    = numpy.std(res)
    data["per0"]   = numpy.percentile(res, 0)
    data["per10"]  = numpy.percentile(res, 10)
    data["per50"]  = numpy.percentile(res, 50)
    data["per90"]  = numpy.percentile(res, 90)
    data["per100"] = numpy.percentile(res, 100)

    # Calculate relative differences:

    res = dbCur.execute("SELECT AVG(linesBefore), AVG(oldFileSize) FROM data WHERE ray_status=2")
    avg = res.fetchone()
    linesBefore = avg[0]
    oldFileSize = avg[1]

    data["averagelinesdiff"] = (data["linesadded"] - data["linesremoved"]) / linesBefore * 100
    data["averagesizediff"] = (data["newfilesize"] - oldFileSize) / oldFileSize * 100
    data["averageraytimediff"] = (data["raytime"] - originalData["rayTime"]) / originalData["rayTime"] * 100

    # Do final tweaks to the data:
    obfName = "$" + dbFile + "$"
    if len(dbFile) > 1:
        obfName = "$" + dbFile[2].upper() + "_{" + dbFile[3:] + "}$"
    data["raytime"] = str(round(data["raytime"] * 1000)) + " ms"
    if len(data["raytime"]) == 7:
        data["raytime"] = data["raytime"][0] + " " + data["raytime"][1:]
    data["linesadded"] = str(round(data["linesadded"], 1))
    data["linesremoved"] = str(round(data["linesremoved"], 1))
    data["newfilesize"] = str(round(data["newfilesize"] / 1000.0, 1)) + " KB"
    data["matches"] = str(round(data["matches"], 1))
    data["averagelinesdiff"] = str(round(data["averagelinesdiff"], 1)) + "\\%"
    data["averagesizediff"] = str(round(data["averagesizediff"], 1)) + "\\%"
    data["averageraytimediff"] = str(round(data["averageraytimediff"], 1)) + "\\%"
    data["avgmatchesshare"] = str(round(data["avgmatchesshare"] * 100, 1)) + "\\%"
    data["std"]    = str(round(data["std"   ], 1)) + "\\%"
    data["per0"]   = str(round(data["per0"  ], 1)) + "\\%"
    data["per10"]  = str(round(data["per10" ], 1)) + "\\%"
    data["per50"]  = str(round(data["per50" ], 1)) + "\\%"
    data["per90"]  = str(round(data["per90" ], 1)) + "\\%"
    data["per100"] = str(round(data["per100"], 1)) + "\\%"

    # Write data to csv:
    csvWriter.writerow([
        obfName,
        data["convstop"],
        data["raystop"],
        data["certain"],
        data["probable"],
        data["unlikely"],
        data["nominer"],
        data["raytime"],
        data["linesadded"],
        data["linesremoved"],
        data["newfilesize"],
        data["matches"],
        data["averagelinesdiff"],
        data["averagesizediff"],
        data['averageraytimediff'],
        data['avgmatchesshare'],
        data['std'],
        data['per0'],
        data['per10'],
        data['per50'],
        data['per90'],
        data['per100']
    ])

    dbCon.close()

getOriginalData()

#'''
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
#'''

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
    2345,
    12345
]

for i in range(len(lst)):
    s = "s/s" + str(lst[i])
    #getFromDb(s)

csvfile.close()
