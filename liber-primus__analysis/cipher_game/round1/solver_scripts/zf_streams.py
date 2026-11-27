"""Under d = c[i]-c[i-1] (inside words) = p*k or p^k: try stream keys (primes, totients, naturals, Fibonacci, GP
values in prime order...) indexed by the global rune index, by the count of in-word positions, or by the word index,
at offsets 0..6000. Also with ratio streams r = c[i]/c[i-1]. Score = IoC of recovered p (English ~1.7)."""
import numpy as np
from load import ct
C=ct()
inv=np.array([0]+[pow(x,27,29) for x in range(1,29)])
D=[];G=[];J=[];W=[];K=[]
g=0;j=0;gw=0
for cl in C:
    for w in cl:
        for k in range(len(w)):
            if k>0: D.append((w[k]-w[k-1])%29); G.append(g); J.append(j); W.append(gw); K.append(k); j+=1
            g+=1
        gw+=1
D=np.array(D);G=np.array(G);J=np.array(J);W=np.array(W);n=len(D)
def primes(N):
    s=np.ones(N+1,bool); s[:2]=0
    for i in range(2,int(N**.5)+1):
        if s[i]: s[i*i::i]=0
    return np.nonzero(s)[0]
P=primes(200000)[:12000]
fib=[1,1]
for _ in range(12000): fib.append((fib[-1]+fib[-2])%29)
streams={'prime':P%29,'totient':(P-1)%29,'n':np.arange(12000)%29,'fib':np.array(fib[:12000]),'prime idx GP?':(P%28)+1,
         'n mod28 +1':np.arange(12000)%28+1}
def ioc_rows(X):
    out=np.zeros(X.shape[0]); m=(X>=0).sum(1)
    for v in range(29):
        cnt=(X==v).sum(1); out+=cnt*(cnt-1)
    return out/(m*(m-1))*29
# power tables: p = d^e, e inverse of k mod 28
powtab=np.array([[pow(x,e,29) if x else 0 for x in range(29)] for e in range(28)])
inv28={k:pow(k,-1,28) for k in range(1,28) if np.gcd(k,28)==1}
res=[]
for sn,s in streams.items():
    for idxn,idx in (('global',G),('inword',J),('word',W)):
        offs=np.arange(0,6000)
        Kk=s[offs[:,None]+idx[None,:]]
        X=(D[None,:]*inv[Kk%29])%29; X[Kk%29==0]=-1
        v=ioc_rows(X); b=v.argmax(); res.append((round(v[b],4),sn,idxn,'mul',int(offs[b])))
        # power
        Kp=Kk%28; ok=np.isin(Kp,list(inv28))
        E=np.zeros_like(Kp)
        for k,e in inv28.items(): E[Kp==k]=e
        X=powtab[E,D[None,:]]; X[~ok]=-1
        v=ioc_rows(X); b=v.argmax(); res.append((round(v[b],4),sn,idxn,'pow',int(offs[b])))
res.sort(reverse=True)
for r in res[:10]: print(r)
