import sqlite3
import matplotlib.pyplot as plt
import numpy as np





# Print entries over limit, but do not include in diagram:
'''
for i in range(0, 20):
    dbEntry = dbCur.execute('SELECT ray_time FROM data WHERE ray_time >= ? AND ray_time < ?', [i, i+1])
    res = dbEntry.fetchall()
    print(f"{i} - {i+1}: {len(res)}")
dbEntry = dbCur.execute('SELECT ray_time FROM data WHERE ray_time >= 20')
res = dbEntry.fetchall()
print(f"{20} -   : {len(res)}")
'''

def gen_diagram(path, name):
    # connect to db
    dbCon = sqlite3.connect(f"saved-db/{path}/{name}.db")
    dbCur = dbCon.cursor()

    # Get data:
    dbEntry = dbCur.execute('SELECT ray_time FROM data WHERE ray_status = 2')
    lst = list(map(lambda x: x[0], dbEntry.fetchall()))

    # Generate diagram
    plt.hist(lst, density=False, bins=20)
    plt.ylabel('Number of samples')
    plt.xlabel('MinerRay running time');
    plt.xlim([0, 20])

    plt.savefig(f'{name}.pdf')

    plt.figure().clear()

    dbCon.close()

gen_diagram('.', '0')

#gen_diagram('d', 'd1')
#gen_diagram('o', 'o1')
#gen_diagram('s', 's4')
#gen_diagram('s', 's12345')
