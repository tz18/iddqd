"""Same-rune rate at distance L split by how many word gaps the pair spans (0 = inside a word), with z vs 1/29."""
import numpy as np
from load import ct, uns
for name,C in (('round1',ct()),('unsolved',uns())):
    c=[];wid=[]
    g=0
    for cl in C:
        for w in cl:
            c+=w; wid+=[g]*len(w); g+=1
    c=np.array(c); wid=np.array(wid)
    print('==',name)
    for L in range(1,9):
        eq=c[L:]==c[:-L]; gaps=wid[L:]-wid[:-L]; row=[]
        for k in range(0,4):
            m=gaps==k; n=m.sum(); e=eq[m].sum(); ex=n/29
            row.append(f'{k}gap {e}/{n}={e/max(n,1)*29:.2f}(z{(e-ex)/np.sqrt(max(ex,1e-9)):+.1f})')
        print(' L',L,' | '.join(row))
