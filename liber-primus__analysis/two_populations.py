import json, collections, math, random
import numpy as np
exec(open('doublets_and_sequences.py').read().split("print('---')")[0].split('def doublets')[0])
IDX={r:i for i,r in enumerate(GP)}
words=[[IDX[r] for r in w] for s in UNS for w in segs[s]]
rng=np.random.default_rng(1)

def feats(ws):
    U=np.zeros((len(ws),29)); M=np.zeros((len(ws),29*29))
    for k,w in enumerate(ws):
        for r in w: U[k,r]+=1
        for a,b in zip(w,w[1:]): M[k,a*29+b]+=1
    return U,M

def em(X, K, iters=200, restarts=5):
    """mixture of multinomials on count rows X; returns best log-likelihood"""
    n,d=X.shape; best=-1e18
    for _ in range(restarts):
        R=rng.dirichlet(np.ones(K),size=n)
        for it in range(iters):
            pi=R.mean(0)+1e-12
            th=(R.T@X)+0.5; th/=th.sum(1,keepdims=True)
            L=X@np.log(th).T+np.log(pi)
            m=L.max(1,keepdims=True); ll=float((m[:,0]+np.log(np.exp(L-m).sum(1))).sum())
            R=np.exp(L-m); R/=R.sum(1,keepdims=True)
        best=max(best,ll)
    return best, R

def gain(ws):
    U,M=feats(ws)
    l1u,_=em(U,1,iters=5,restarts=1); l2u,Ru=em(U,2)
    l1m,_=em(M,1,iters=5,restarts=1); l2m,Rm=em(M,2,iters=100,restarts=3)
    return l2u-l1u, l2m-l1m, Ru

gu,gm,Ru=gain(words)
print('real: 2-group gain  unigram %.1f   transitions %.1f'%(gu,gm))
print('  group sizes (unigram split):', np.round(Ru.sum(0)).astype(int))
flat=[r for w in words for r in w]; lens=[len(w) for w in words]
nu=[];nm=[]
for rep in range(30):
    f=flat[:]; random.shuffle(f); ws=[];i=0
    for L in lens: ws.append(f[i:i+L]); i+=L
    a,b,_=gain(ws); nu.append(a); nm.append(b)
print('shuffled (30x): unigram gain %.1f ± %.1f (max %.1f)   transitions %.1f ± %.1f (max %.1f)'%(np.mean(nu),np.std(nu),max(nu),np.mean(nm),np.std(nm),max(nm)))

# per-page heterogeneity of rune frequencies and of doublet rate (continuous stream)
pages=collections.defaultdict(list)
for p in d['pages']:
    for l in p['lines']:
        if 7<=l['s']<=15:
            for t in l['t']:
                if t[0]=='r': pages[p['page']].append(IDX[t[1]])
tab=np.array([np.bincount(v,minlength=29) for v in pages.values()])
E=tab.sum(1,keepdims=True)*tab.sum(0,keepdims=True)/tab.sum()
chi=((tab-E)**2/E).sum(); df=(tab.shape[0]-1)*28
print('rune frequency across %d pages: chi2 %.0f on %d df  (z=%.2f)'%(tab.shape[0],chi,df,(chi-df)/math.sqrt(2*df)))
dbl=np.array([sum(a==b for a,b in zip(v,v[1:])) for v in pages.values()]); tr=np.array([len(v)-1 for v in pages.values()])
rate=dbl.sum()/tr.sum(); Ed=tr*rate
chid=((dbl-Ed)**2/Ed).sum()
print('doublets per page: total %d, chi2 %.1f on %d df (z=%.2f)'%(dbl.sum(),chid,len(dbl)-1,(chid-(len(dbl)-1))/math.sqrt(2*(len(dbl)-1))))
