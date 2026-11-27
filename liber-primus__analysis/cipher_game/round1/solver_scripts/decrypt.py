"""Round-1 decryption. Usage: python3 decrypt.py [out.txt]
Cipher: c[i] = c[i-1] + p[i] * q[i]  (mod 29), c[-1] = 0, where q[i] is the i-th prime (from 2) with 29 left out,
i = global rune index (word and clause breaks are kept and do not affect the key).
Decryption: p[i] = (c[i] - c[i-1]) * q[i]^-1 mod 29."""
import numpy as np, sys
from load import ct
LAT='F U TH O R C G W H N I J EO P X S T B E M L NG OE D A AE Y IA EA'.split()
C=ct()
def primes(N):
    s=np.ones(N+1,bool); s[:2]=0
    for i in range(2,int(N**.5)+1):
        if s[i]: s[i*i::i]=0
    return [int(p) for p in np.nonzero(s)[0] if p!=29]
Q=primes(100000)
inv=[0]+[pow(x,27,29) for x in range(1,29)]
g=0; prev=0; lines=[]; P=[]
for cl in C:
    ws=[]
    for w in cl:
        s=[]
        for r in w:
            p=((r-prev)*inv[Q[g]%29])%29; P.append(p)
            s.append(LAT[p]); prev=r; g+=1
        ws.append(''.join(s))
    lines.append(' '.join(ws))
# self-check: re-encrypt
c=0; ok=True; g=0
flat=[r for cl in C for w in cl for r in w]
for i,p in enumerate(P):
    c=(c+p*Q[i])%29; ok&=(c==flat[i])
print('re-encryption matches ciphertext:',ok, file=sys.stderr)
txt='\n'.join(lines)+'\n'
if len(sys.argv)>1: open(sys.argv[1],'w').write(txt)
else: print(txt)
