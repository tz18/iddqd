import collections, numpy as np
from load import ct
LAT='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
C=ct(); rs=[];wpos=[];cl=[]
for ci,c in enumerate(C):
    for wi,w in enumerate(c):
        for k,r in enumerate(w): rs.append(r); wpos.append(k); cl.append(ci)
N=len(rs)
for n in (3,4,5):
    d=collections.defaultdict(list)
    for i in range(N-n+1): d[tuple(rs[i:i+n])].append(i)
    rep={k:v for k,v in d.items() if len(v)>1}
    print(n,'grams repeated:',len(rep))
    if n>=4:
        for k,v in rep.items(): print('  ','-'.join(LAT[x] for x in k),v,[v[j+1]-v[0] for j in range(len(v)-1)],'wpos',[wpos[i] for i in v],'clauses',[cl[i] for i in v])
# expected number of repeated trigrams for random
# repeated whole words
wd=collections.defaultdict(list)
ws=[(ci,wi,tuple(w)) for ci,c in enumerate(C) for wi,w in enumerate(c)]
for ci,wi,w in ws: wd[w].append((ci,wi))
print('repeated words:',[( '-'.join(LAT[x] for x in w),v) for w,v in wd.items() if len(v)>1])
