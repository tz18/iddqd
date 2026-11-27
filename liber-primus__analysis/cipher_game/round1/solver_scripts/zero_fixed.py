"""Hypothesis family: inside words, d[i] = c[i] - c[i-1] = f_k(p[i]) with f_k fixing 0 (multiply by k, or power k),
so in-word doublets happen only for plaintext F. Tests: (1) grouped IoC of d by context (position in word, previous
rune, global index mod m...); (2) multiplicative ratios r = c[i]/c[i-1]; (3) stream keys k_j (primes, naturals,
Fibonacci...) at any offset: p = d / k_j or p = d^(1/k_j)."""
import numpy as np, collections
from load import ct
rng=np.random.default_rng(0)
C=ct()
inv=[0]+[pow(x,27,29) for x in range(1,29)]
rows=[];g=0;gw=0
for ci,cl in enumerate(C):
    for wi,w in enumerate(cl):
        for k in range(len(w)):
            if k>0: rows.append(dict(d=(w[k]-w[k-1])%29,r=(w[k]*inv[w[k-1]])%29 if w[k-1] else -1,c=w[k],prev=w[k-1],k=k,L=len(w),g=g,gw=gw,ci=ci,wi=wi))
            g+=1
        gw+=1
def gioc(vals,ctx):
    gr=collections.defaultdict(list)
    for v,c in zip(vals,ctx): gr[c].append(v)
    num=den=0
    for v in gr.values():
        if len(v)<2: continue
        cnt=np.bincount(v,minlength=29); num+=(cnt*(cnt-1)).sum(); den+=len(v)*(len(v)-1)
    return num/den*29
d=[r['d'] for r in rows]
print('in-word diffs n=%d, zeros %d'%(len(d),d.count(0)))
ctxs={'all':[0]*len(rows),'pos in word':[r['k'] for r in rows],'prev rune':[r['prev'] for r in rows],'cur rune':[r['c'] for r in rows],
      'word len':[r['L'] for r in rows],'clause':[r['ci'] for r in rows],'word':[r['gw'] for r in rows],'word idx in clause':[r['wi'] for r in rows]}
for m in range(2,30): ctxs[f'g mod {m}']=[r['g']%m for r in rows]
for nm,ctx in ctxs.items():
    v=gioc(d,ctx); ctrl=[gioc(d,[ctx[j] for j in rng.permutation(len(ctx))]) for _ in range(20)]
    z=(v-np.mean(ctrl))/(np.std(ctrl)+1e-9)
    if abs(z)>2 or nm in('all','pos in word','prev rune','word'): print(f'  d grouped by {nm:20s} {v:.4f} ctrl {np.mean(ctrl):.4f} z {z:+.1f}')
rr=[r['r'] for r in rows if r['r']>=0]
cnt=np.bincount(rr,minlength=29); print('ratio c/c_prev IoC', (cnt*(cnt-1)).sum()/(len(rr)*(len(rr)-1))*29, 'ratio==1 count',cnt[1],'of',len(rr))
