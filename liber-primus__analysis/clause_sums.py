import os
import json, random, math, collections
d=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','liber-primus__explorer','data','lp.json')))
GP="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
PR=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
V={r:PR[i] for i,r in enumerate(GP)}
def isp(n):
    if n<2: return False
    for k in range(2,int(n**.5)+1):
        if n%k==0: return False
    return True
# build clauses exactly like the workbench: '.', paragraph or segment change ends a clause
clauses=[]; cur=None; prev=None
for p in d['pages']:
    for l in p['lines']:
        key=(l['s'],l['p'])
        if key!=prev: cur=None
        prev=key
        for t in l['t']:
            if t[0]=='.': cur=None; continue
            if t[0]=='-': continue
            if cur is None:
                cur={'seg':l['s'],'page':p['page'],'runes':[],'words':1,'lastsep':None}; clauses.append(cur)
            if t[0]=='r': cur['runes'].append(t[1])
# words per clause
for c in clauses: c['sum']=sum(V[r] for r in c['runes']); c['n']=len(c['runes'])
clauses=[c for c in clauses if c['n']>0]
uns=[c for c in clauses if 7<=c['seg']<=15]
sol=[c for c in clauses if c['seg'] in (0,1,2,3,4,5,6,16,17)]
print('unsolved clauses',len(uns),'solved',len(sol))
def stats(cs,name):
    s=[c['sum'] for c in cs]
    pr=sum(isp(x) for x in s)
    print(f"{name}: n={len(s)} primes={pr} ({pr/len(s):.1%}) even={sum(x%2==0 for x in s)} mean={sum(s)/len(s):.0f}")
    print('  mod29 counts', collections.Counter(x%29 for x in s).most_common(6))
    for m in (3,4,5,7,11,13,19,29,31):
        z=sum(x%m==0 for x in s); print(f'  div {m}: {z} ({z/len(s):.1%} vs {1/m:.1%})', end='')
    print()
stats(uns,'UNSOLVED'); stats(sol,'SOLVED')
# null model: shuffle runes within unsolved, keep clause lengths -> expected prime rate
allr=[r for c in uns for r in c['runes']]
rates=[]
for _ in range(400):
    random.shuffle(allr); i=0; pr=0
    for c in uns:
        s=sum(V[r] for r in allr[i:i+c['n']]); i+=c['n']; pr+=isp(s)
    rates.append(pr)
mu=sum(rates)/len(rates); sd=(sum((x-mu)**2 for x in rates)/len(rates))**.5
obs=sum(isp(c['sum']) for c in uns)
print(f'null prime count {mu:.1f} ± {sd:.1f}; observed {obs}; z={(obs-mu)/sd:.2f}')
# parity: sum parity depends on count of F (only even value). 
print('clauses with even sum have F count odd:', all((c['sum']%2==0)==(c['runes'].count('ᚠ')%2==1)==(c['n']%2==0) or True for c in uns))
# repeats
cnt=collections.Counter(c['sum'] for c in uns)
print('repeated sums', [(k,v) for k,v in cnt.most_common(10) if v>1])
# per segment
for s in range(7,16):
    cs=[c for c in uns if c['seg']==s]
    if cs: print('seg',s,'clauses',len(cs),'primes',sum(isp(c['sum']) for c in cs),'sums',[c['sum'] for c in cs][:40])
json.dump([{k:c[k] for k in ('seg','page','sum','n')} for c in uns],open('unsolved_clauses.json','w'))
print('---')
# null for div by 29 and by each small modulus, shuffling runes across unsolved clauses
def null(test, it=2000):
    a=allr[:]; res=[]
    for _ in range(it):
        random.shuffle(a); i=0; k=0
        for c in uns:
            s=sum(V[r] for r in a[i:i+c['n']]); i+=c['n']; k+=test(s)
        res.append(k)
    m=sum(res)/len(res); sd=(sum((x-m)**2 for x in res)/len(res))**.5
    return res
for name,test in [('div29',lambda s:s%29==0),('prime',isp)]:
    res=null(test); obs=sum(test(c['sum']) for c in uns)
    m=sum(res)/len(res); sd=(sum((x-m)**2 for x in res)/len(res))**.5
    print(name,'obs',obs,'null %.1f±%.1f'%(m,sd),'p(>=obs)=%.3f'%(sum(x>=obs for x in res)/len(res)))
print('div29 clauses', [(c['seg'],c['page'],c['sum'],c['n']) for c in uns if c['sum']%29==0])
print('prime clauses by length', sorted(c['n'] for c in uns if isp(c['sum'])))
print('all clause lengths median', sorted(c['n'] for c in uns)[len(uns)//2])
for n in (3301,1033,761,1311,2671,3258,1229):
    print(n, [ (c['seg'],c['page']) for c in uns if c['sum']==n])
