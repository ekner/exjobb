import numpy as np
import matplotlib.pyplot as plt
from operator import add

plt.rcParams['text.usetex'] = True


#N = 13
#certain = [13,0,0,0,0,0,0,0,0,15,14,15,15]
#probable = [77,3,0,0,0,0,0,0,3,98,100,75,99]
#unlikely = [123,0,0,0,0,0,0,0,0,77,79,80,80]

#N = 11
#certain = [13,0,0,0,0,15,15,15,15,15,15]
#probable = [77,3,0,0,0,98,75,99,75,97,75]
#unlikely = [123,0,0,0,0,76,75,76,76,80,79]

#N = 11
#certain = [13,0,0,0,0,0,0,15,15,15,14]
#probable = [77,0,0,0,0,0,0,73,99,75,75]
#unlikely = [123,0,0,0,0,0,0,74,75,75,76]

N = 7
certain = [13,0,0,0,0,14,0]
probable = [77,0,0,3,3,69,0]
unlikely = [123,0,0,0,0,74,0]


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


#plt.xticks(ind, ('$\emptyset$', '$D_1$', '$D_2$', '$D_3$', '$D_4$', '$O_1$', '$O_2$', '$O_3$', '$S_1$', '$S_2$', '$S_3$', '$S_4$', '$S_5$'))
#plt.xticks(ind, ('$\emptyset$', '$S_{12}$', '$S_{13}$', '$S_{14}$', '$S_{15}$', '$S_{23}$', '$S_{24}$', '$S_{25}$', '$S_{34}$', '$S_{35}$', '$S_{45}$'))
#plt.xticks(ind, ('$\emptyset$', '$S_{123}$', '$S_{124}$', '$S_{125}$', '$S_{134}$', '$S_{135}$', '$S_{145}$', '$S_{234}$', '$S_{235}$', '$S_{245}$', '$S_{345}$'))
plt.xticks(ind, ('$\emptyset$', '$S_{1234}$', '$S_{1235}$', '$S_{1245}$', '$S_{1345}$', '$S_{2345}$', '$S_{12345}$'))


plt.yticks(np.arange(0, 213, 20))


#plt.legend((p1[0], p2[0], p3[0]), ('Certain', 'Probable', 'Unlikely'), loc='upper center')
#plt.legend((p1[0], p2[0], p3[0]), ('Certain', 'Probable', 'Unlikely'), loc='upper center', bbox_to_anchor=(0.28, 1))
#plt.legend((p1[0], p2[0], p3[0]), ('Certain', 'Probable', 'Unlikely'), loc='upper center')
plt.legend((p1[0], p2[0], p3[0]), ('Certain', 'Probable', 'Unlikely'), loc='upper center')


plt.savefig('bar-results-S45.pdf')
#plt.show()
