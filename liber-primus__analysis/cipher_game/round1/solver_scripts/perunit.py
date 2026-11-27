"""Within-unit pair equality: are two values from the same word (or clause) equal more often than chance?
Applied to raw runes and to in-word differences (c[i]-c[i-1]) and sums. A per-word (or per-clause) Caesar shift on
English, or on an autokey-removed stream, gives ~1.7/29."""
import numpy as np, itertools
from load import ct, uns
def rate(units):
    eq=n=0
    for u in units:
        for a,b in itertools.combinations(u,2): n+=1; eq+=a==b
    return eq/max(n,1)*29, n
for name,C in (('round1',ct()),('unsolved',uns())):
    ws=[w for c in C for w in c]
    raw=[w for w in ws]; dif=[[(w[i]-w[i-1])%29 for i in range(1,len(w))] for w in ws]
    sm=[[(w[i]+w[i-1])%29 for i in range(1,len(w))] for w in ws]
    cl=[[r for w in c for r in w] for c in C]
    cd=[[(x[i]-x[i-1])%29 for i in range(1,len(x))] for x in cl]
    print(name,'raw/word',rate(raw),'diff/word',rate(dif),'sum/word',rate(sm),'raw/clause',rate(cl),'diff/clause',rate(cd))
