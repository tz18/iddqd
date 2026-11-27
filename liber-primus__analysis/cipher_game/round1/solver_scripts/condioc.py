"""Conditional IoC: pool same-rune pair counts of c[i] within groups defined by a context (previous rune, rune two back,
position in word, word length, (length,position), clause index, word index mod m...). If the substitution alphabet is
selected by that context, grouped IoC rises toward English (~1.7). Compared with random-group control by permuting
contexts."""
import numpy as np, collections
from load import ct, uns
rng=np.random.default_rng(0)
def gioc(vals,ctx):
    g=collections.defaultdict(list)
    for v,c in zip(vals,ctx): g[c].append(v)
    num=den=0
    for v in g.values():
        if len(v)<2: continue
        cnt=np.bincount(v,minlength=29); num+=(cnt*(cnt-1)).sum(); den+=len(v)*(len(v)-1)
    return num/den*29
def run(C,name):
    rows=[]
    for ci,c in enumerate(C):
        for wi,w in enumerate(c):
            for k,r in enumerate(w): rows.append(dict(c=r,ci=ci,wi=wi,k=k,L=len(w),kr=len(w)-1-k))
    vals=[r['c'] for r in rows]; N=len(rows)
    ctxs={
     'prev rune':[None]+vals[:-1],
     'prev rune (same word)':[rows[i-1]['c'] if i and rows[i]['k']>0 else -1 for i in range(N)],
     'rune two back':[None,None]+vals[:-2],
     'next rune':vals[1:]+[None],
     'pos in word':[r['k'] for r in rows],
     'word length':[r['L'] for r in rows],
     '(len,pos)':[r['L']*100+r['k'] for r in rows],
     'pos from end':[r['kr'] for r in rows],
     'word first rune':[C[r['ci']][r['wi']][0] if r['k']>0 else -1 for r in rows],
     'clause':[r['ci'] for r in rows],
     'word index in clause':[r['wi'] for r in rows],
    }
    gw=0; wid=[]
    for ci,c in enumerate(C):
        for w in c:
            wid+= [gw]*len(w); gw+=1
    ctxs['word']=wid
    for m in (2,3,5,7,11,13):
        ctxs[f'word# mod {m}']=[x%m for x in wid]
    print('==',name)
    for k,ctx in ctxs.items():
        v=gioc(vals,ctx); ctrl=[gioc(vals,[ctx[j] for j in rng.permutation(len(ctx))]) for _ in range(30)]
        print(f'  {k:24s} {v:.4f}  control {np.mean(ctrl):.4f} sd {np.std(ctrl):.4f}  z {(v-np.mean(ctrl))/np.std(ctrl):+.1f}')
run(ct(),'round1')
