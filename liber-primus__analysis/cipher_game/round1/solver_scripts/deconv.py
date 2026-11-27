"""If c = p + k, in-word cipher differences = plaintext differences (+) key steps (circular convolution mod 29).
Estimate the key-step distribution S by least squares / EM deconvolution given English in-word difference
distribution from the solved LP plaintext."""
import sys, numpy as np, collections
sys.path.insert(0,'/home/user/iddqd/liber-primus__analysis')
from lp_common import R,d
from load import ct
sol=[r for r in R if d['segments'][r['seg']]['solved'] and r['p'] is not None]
ws=collections.OrderedDict()
for r in sol: ws.setdefault(r['word'],[]).append(r['p'])
pd=np.zeros(29)
for w in ws.values():
    for i in range(1,len(w)): pd[(w[i]-w[i-1])%29]+=1
pd/=pd.sum(); print('English in-word diff dist (x29):',np.round(pd*29,2))
print('IoC of English diffs',(pd**2).sum()*29)
C=ct(); cd=np.zeros(29)
for c in C:
    for w in c:
        for i in range(1,len(w)): cd[(w[i]-w[i-1])%29]+=1
n=cd.sum()
# EM for S: cd[j] ~ n * sum_s S[s] pd[j-s]
S=np.ones(29)/29
for it in range(3000):
    M=np.array([[pd[(j-s)%29] for s in range(29)] for j in range(29)])
    pred=M@S; S=S*(M.T@(cd/pred))/n
print('estimated step dist (x29):',np.round(S*29,2))
# loglik gain over uniform
ll=lambda q:(cd*np.log(q)).sum()
print('LL gain vs uniform', ll(M@S)-ll(np.ones(29)/29))
