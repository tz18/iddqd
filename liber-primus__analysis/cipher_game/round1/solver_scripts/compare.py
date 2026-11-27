"""Measure the brief's 12 findings (plus extras) on the round-1 ciphertext and on the unsolved pages.
Uncertainty: the same statistic on 400 random contiguous ~600-word blocks of the unsolved pages (clause-aligned)."""
import numpy as np, collections, math
from load import ct, uns, VAL
rng=np.random.default_rng(1)
def isprime(n):
    if n<2: return False
    for p in range(2,int(n**.5)+1):
        if n%p==0: return False
    return True
def flat(cls): return [r for c in cls for w in c for r in w]
def words(cls): return [w for c in cls for w in c]
def stats(cls):
    S={}
    rs=np.array(flat(cls)); ws=words(cls); N=len(rs)
    # 1 doublets
    inw=sum(sum(w[i]==w[i+1] for i in range(len(w)-1)) for w in ws); nin=sum(len(w)-1 for w in ws)
    acr=sum(ws[i][-1]==ws[i+1][0] for i in range(len(ws)-1)); nac=len(ws)-1
    S['dbl_all']=(inw+acr)/(nin+nac); S['dbl_in']=inw/nin; S['dbl_gap']=acr/nac
    S['n_dbl']=inw+acr
    # 2 doublet place (pair starting at 0 = first, pair ending at last = last, else middle; L=2 -> first)
    pos=collections.Counter(); exp=collections.Counter()
    for w in ws:
        L=len(w)
        for i in range(L-1):
            k='first' if i==0 else ('last' if i==L-2 else 'mid')
            exp[k]+=1
            if w[i]==w[i+1]: pos[k]+=1
    t=sum(pos.values()) or 1; te=sum(exp.values())
    for k in ('first','mid','last'): S['dpos_'+k]=pos[k]/t; S['dpos_exp_'+k]=exp[k]/te
    # 3 frequencies
    cnt=np.bincount(rs,minlength=29); e=N/29
    S['chi2']=((cnt-e)**2/e).sum(); S['meanGP']=np.mean([VAL[r] for r in rs])
    S['ioc']=(cnt*(cnt-1)).sum()/(N*(N-1))*29
    # 4 F
    S['F']=cnt[0]/N
    # 5 word lengths
    L=np.array([len(w) for w in ws])
    for k in range(1,10): S[f'wl{k}']=(L==k).mean()
    S['wl10+']=(L>=10).mean(); S['wl_mean']=L.mean()
    # 6 order
    lc=[]
    for c in cls:
        l=[len(w) for w in c]; lc.append(l)
    x=[];y=[]
    for l in lc:
        for i in range(len(l)-1): x.append(l[i]); y.append(l[i+1])
    S['wl_lag1']=np.corrcoef(x,y)[0,1]
    S['final_len']=np.mean([l[-1] for l in lc if len(l)>1]); S['first_len']=np.mean([l[0] for l in lc if len(l)>1])
    # 7 lag-5 inside words and across
    pe=((cnt/N)**2).sum()
    for lag in (1,2,3,4,5,6,7,8):
        eq=n=0
        for w in ws:
            for i in range(len(w)-lag): n+=1; eq+=w[i]==w[i+lag]
        S[f'in_lag{lag}']=eq/max(n,1); S[f'in_lag{lag}_n']=n
    wid=np.concatenate([np.full(len(w),i) for i,w in enumerate(ws)])
    m=wid[5:]!=wid[:-5]; S['ac_lag5']=(rs[5:]==rs[:-5])[m].mean()
    S['pe']=pe
    # 8 prime short clauses
    sh=[c for c in cls if sum(len(w) for w in c)<=31]
    S['short_n']=len(sh); S['short_prime']=sum(isprime(sum(VAL[r] for w in c for r in w)) for c in sh)
    allp=sum(isprime(sum(VAL[r] for w in c for r in w)) for c in cls); S['all_prime_frac']=allp/len(cls)
    # 9 clause lengths
    cw=np.array([len(c) for c in cls]); S['clause_words_mean']=cw.mean(); S['clause_words_sd']=cw.std(); S['one_word']=int((cw==1).sum())
    S['clause_n']=len(cls)
    # 12 repeats: longest repeated run
    s=''.join(chr(65+r) for r in rs); best=0
    for k in range(4,12):
        seen=set(); hit=False
        for i in range(N-k+1):
            q=s[i:i+k]
            if q in seen: hit=True;break
            seen.add(q)
        if hit: best=k
        else: break
    S['longest_repeat']=best
    return S
U=uns(); C=ct()
SU=stats(U); SC=stats(C)
nw=len(words(C))
# blocks of unsolved with ~ same number of words, clause aligned
blocks=[]
for _ in range(400):
    st=rng.integers(len(U)); b=[];k=0;i=st
    while k<nw: b.append(U[i%len(U)]); k+=len(U[i%len(U)]); i+=1
    blocks.append(stats(b))
print(f'{"stat":18s} {"unsolved":>9s} {"block mean":>10s} {"block sd":>9s} {"round1":>9s} {"z":>6s} {"pct":>5s}')
for k in SU:
    bv=np.array([b[k] for b in blocks],float); z=(SC[k]-bv.mean())/(bv.std()+1e-12); pct=(bv<SC[k]).mean()+0.5*(bv==SC[k]).mean()
    print(f'{k:18s} {SU[k]:9.4f} {bv.mean():10.4f} {bv.std():9.4f} {SC[k]:9.4f} {z:6.2f} {pct:5.3f}')
