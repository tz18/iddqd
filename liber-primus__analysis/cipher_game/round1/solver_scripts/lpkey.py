"""Running keys taken from the Liber Primus itself: the whole LP rune stream (ciphertext as printed), the solved
plaintext, each forwards and reversed, GP values mod 29 of them, at every offset; c-k, k-c, c+k. Score: IoC."""
import sys, numpy as np
sys.path.insert(0,'/home/user/iddqd/liber-primus__analysis')
from lp_common import R,d
from load import ct, VAL
C=ct(); c=np.array([r for cl in C for w in cl for r in w]); N=len(c)
allc=np.array([r['c'] for r in R]); solp=np.array([r['p'] for r in R if d['segments'][r['seg']]['solved'] and r['p'] is not None])
V=np.array(VAL)
keys={'LP runes':allc,'LP runes rev':allc[::-1],'solved plain':solp,'solved plain rev':solp[::-1],
      'LP GPval':V[allc]%29,'solved plain GPval':V[solp]%29}
def ioc_rows(X):
    out=np.zeros(X.shape[0])
    for v in range(29):
        cnt=(X==v).sum(1); out+=cnt*(cnt-1)
    return out/(N*(N-1))*29
res=[]
for name,k in keys.items():
    kk=np.concatenate([k,k])  # wrap
    for start in range(0,len(k),2000):
        offs=np.arange(start,min(start+2000,len(k)))
        K=kk[offs[:,None]+np.arange(N)[None,:]] if len(kk)>=len(k)+N else None
        if K is None: break
        for op,X in (('c-k',(c-K)%29),('c+k',(c+K)%29)):
            v=ioc_rows(X); j=v.argmax(); res.append((round(v[j],4),name,op,int(offs[j])))
res.sort(reverse=True); print(res[:10])
