"""Known-stream keys: p = s*(c - k[j]) style decryptions (c = p + k, c = k - p, c = p - k), key index j = global
rune index + offset (0..20000), or restarting at each clause (offset 0..200). IoC of the result is the score
(English ~1.7; flat 1.0). Streams: primes, totient (p-1), Fibonacci, naturals, squares, triangular, GP values of
consecutive primes indexes, pi and e digits (base 10)."""
import numpy as np, math
from load import ct
C=ct(); c=np.array([r for cl in C for w in cl for r in w]); N=len(c)
def primes(n):
    s=np.ones(n+1,bool); s[:2]=0
    for i in range(2,int(n**.5)+1):
        if s[i]: s[i*i::i]=0
    return np.nonzero(s)[0]
P=primes(400000)[:30000]
M=30000
fib=[0,1]
for _ in range(M): fib.append((fib[-1]+fib[-2])%29)
streams={
 'prime':P%29,'totient':(P-1)%29,'prime+1':(P+1)%29,'fib':np.array(fib[:M]),'n':np.arange(M)%29,
 'n^2':(np.arange(M)**2)%29,'tri':(np.arange(M)*(np.arange(M)+1)//2)%29,
 'prime_gap':np.diff(P)[:M-1]%29,
}
def ioc_rows(X):
    # X: (k,N) -> IoC per row
    out=np.zeros(X.shape[0])
    for v in range(29):
        cnt=(X==v).sum(1); out+=cnt*(cnt-1)
    return out/(N*(N-1))*29
best=[]
for name,k in streams.items():
    offs=np.arange(0,len(k)-N)
    idx=offs[:,None]+np.arange(N)[None,:]
    K=k[idx]
    for op,f in (('c-k',lambda K:(c-K)%29),('k-c',lambda K:(K-c)%29)):
        v=ioc_rows(f(K)); j=v.argmax(); best.append((v[j],name,op,'global',int(offs[j])))
    # restart per clause
    cl_start=[];i=0
    pos=[]
    for cl in C:
        L=sum(len(w) for w in cl); pos+=list(range(L))
    pos=np.array(pos)
    for off in range(0,300):
        for op in (1,-1):
            x=(op*(c-k[pos+off]))%29; cnt=np.bincount(x,minlength=29)
            best.append(((cnt*(cnt-1)).sum()/(N*(N-1))*29,name,'c-k' if op==1 else 'k-c','clause-restart',off))
best.sort(reverse=True)
for b in best[:15]: print(b)
