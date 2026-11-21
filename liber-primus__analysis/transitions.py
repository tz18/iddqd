import json, collections, math, random
exec(open('doublets_and_sequences.py').read().split("print('---')")[0].split('def doublets')[0])
IDX={r:i for i,r in enumerate(GP)}
# continuous stream per segment (word gaps ignored), unsolved only
T=[[0]*29 for _ in range(29)]
for s in UNS:
    st=[IDX[r] for w in segs[s] for r in w]
    for a,b in zip(st,st[1:]): T[a][b]+=1
N=sum(map(sum,T))
row=[sum(T[i]) for i in range(29)]; col=[sum(T[i][j] for i in range(29)) for j in range(29)]
# expected under "no self edges, otherwise proportional to column freq" (user's model)
diag=sum(T[i][i] for i in range(29))
print('transitions',N,'self',diag, 'self rate %.4f'%(diag/N))
# chi-square of off-diagonal vs model: E_ij = row_i * col_j / (N_offdiag-adjusted)
chi=0; df=0; resid=[]
for i in range(29):
    tot_off=row[i]-T[i][i]
    w=[col[j] if j!=i else 0 for j in range(29)]; sw=sum(w)
    for j in range(29):
        if j==i: continue
        e=tot_off*w[j]/sw; chi+=(T[i][j]-e)**2/e; df+=1; resid.append(((T[i][j]-e)/math.sqrt(e),GP[i]+GP[j],T[i][j],round(e,1)))
df-=29+28  # rough
print('off-diagonal chi2 %.1f on ~%d df'%(chi,df))
resid.sort()
print('most under-represented', resid[:8]); print('most over', resid[-8:])
# simple uniform-ness of row/col frequencies
print('rune freq min/max', min(col), max(col), 'mean', N/29)
json.dump({'runes':[g for g in GP],'T':T},open('transitions.json','w'))
