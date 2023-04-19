import numpy as np
import matplotlib.pyplot as plt
from operator import add

plt.rcParams['text.usetex'] = True

N = 13

certain = [13,0,0,0,0,0,0,0,0,15,14,15,15]
probable = [77,3,0,0,0,0,0,0,3,98,100,75,99]
unlikely = [123,0,0,0,0,0,0,0,0,77,79,80,80]
ind = np.arange(N)
width = 0.4

assert(len(certain) == N)
assert(len(probable) == N)
assert(len(unlikely) == N)

fig = plt.subplots(figsize = (6, 5))
p1 = plt.bar(ind, certain, width, color='red')
p2 = plt.bar(ind, probable, width, bottom = certain, color='orange')
p3 = plt.bar(ind, unlikely, width, bottom = list(map(add, certain, probable)), color='gray')

plt.ylabel('Number of samples')
plt.xlabel('Obfuscation type')
#plt.title('Contribution by the teams')
plt.xticks(ind, ('$\emptyset$', '$D_1$', '$D_2$', '$D_3$', '$D_4$', '$O_1$', '$O_2$', '$O_3$', '$S_1$', '$S_2$', '$S_3$', '$S_4$', '$S_5$'))
plt.yticks(np.arange(0, 213, 20))
plt.legend((p1[0], p2[0], p3[0]), ('Certain', 'Probable', 'Unlikely'), loc='upper center')

plt.savefig('bar-results.pdf')
#plt.show()
