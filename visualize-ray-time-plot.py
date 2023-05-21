import sqlite3
import matplotlib.pyplot as plt
import numpy as np

print("x, y")

def gen_diagram(path, name):
    # connect to db
    dbCon = sqlite3.connect(f"saved-db/{path}/{name}.db")
    dbCur = dbCon.cursor()

    dbConBase = sqlite3.connect(f"saved-db/first-total-run.db")
    dbCurBase = dbConBase.cursor()

    # Get data:
    dbEntry = dbCur.execute('SELECT ray_time FROM data WHERE ray_status = 2')
    yVal = list(map(lambda x: x[0], dbEntry.fetchall()))

    ids = dbCur.execute('SELECT id FROM data WHERE ray_status = 2').fetchall()
    xVal = []

    for i in range(len(ids)):
        x = dbCurBase.execute('SELECT ray_time FROM data WHERE id = ?', ids[i]).fetchall()[0]
        xVal.append(x)

    #plt.plot(xVal, yVal, 'ro')
    #plt.plot([0, 20], [0, 20], 'gray', linestyle='dashed')

    for i in range(len(xVal)):
        print(str(xVal[i][0]) + "," + str(yVal[i])) 

    #plt.ylabel('Obfuscated running time')
    #plt.xlabel('Original running time')
    #plt.savefig(f'{name}-plot.pdf')
    #plt.figure().clear()

    dbCon.close()

#gen_diagram('.', '0')
#gen_diagram('d', 'd1')
#gen_diagram('o', 'o1')
#gen_diagram('s', 's4')
#gen_diagram('s', 's12345')

gen_diagram('s', 's1')
