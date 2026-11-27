import numpy as np, collections
from load import ct, uns
def ioc(x):
    x=np.asarray(x); n=len(x)
    if n<2: return float('nan')
    c=np.bincount(x,minlength=29); return (c*(c-1)).sum()/(n*(n-1))*29
for name,C in (('round1',ct()),('unsolved',uns())):
    ws=[w for c in C for w in c]; rs=np.array([r for w in ws for r in w])
    print('==',name)
    for p in range(6): print(' pos-in-word',p,'IoC %.3f n=%d'%(ioc([w[p] for w in ws if len(w)>p]),sum(len(w)>p for w in ws)))
    print(' last rune IoC %.3f'%ioc([w[-1] for w in ws]))
    print(' clause-first rune IoC %.3f'%ioc([c[0][0] for c in C]), ' clause-first word first rune counts', sorted(collections.Counter(c[0][0] for c in C).most_common(5)))
    din=[ (w[i+1]-w[i])%29 for w in ws for i in range(len(w)-1)]
    dac=[ (ws[i+1][0]-ws[i][-1])%29 for i in range(len(ws)-1)]
    print(' in-word diff IoC %.3f, gap diff IoC %.3f'%(ioc(din),ioc(dac)))
    for sign in (1,-1):
      s=[(w[i+1]+sign*w[i])%29 if sign==1 else (w[i+1]-w[i])%29 for w in ws for i in range(len(w)-1)]
    sm=[(w[i+1]+w[i])%29 for w in ws for i in range(len(w)-1)]; print(' in-word sum IoC %.3f'%ioc(sm))
    # periodic scan, raw and diff
    D=(rs[1:]-rs[:-1])%29
    for lab,x in (('raw',rs),('diff',D)):
        res=[]
        for P in range(1,101):
            v=np.mean([ioc(x[j::P]) for j in range(P)]); res.append((v,P))
        res.sort(reverse=True); print(' ',lab,'top periods',[(P,round(v,3)) for v,P in res[:5]])
    # position-in-clause key (restart each clause)
    for P in (0,):
        pc=collections.defaultdict(list)
        for c in C:
            fl=[r for w in c for r in w]
            for i,r in enumerate(fl): pc[i].append(r)
        print(' pos-in-clause IoC (0..5):',[round(ioc(pc[i]),3) for i in range(6)])
