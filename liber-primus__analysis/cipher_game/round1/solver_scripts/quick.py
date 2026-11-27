import json,collections,numpy as np
C=json.load(open('../ciphertext.json'))['clauses']
runes=[r for cl in C for w in cl for r in w]
words=[w for cl in C for w in cl]
N=len(runes); print('runes',N,'words',len(words),'clauses',len(C))
cnt=collections.Counter(runes); print(sorted(cnt.items()))
ioc=sum(v*(v-1) for v in cnt.values())/(N*(N-1))*29; print('IoC',ioc)
d=sum(runes[i]==runes[i+1] for i in range(N-1)); print('doublets',d,d/(N-1))
for lag in range(1,13):
  print(lag, sum(runes[i]==runes[i+lag] for i in range(N-lag))/(N-lag)*29)
