import os
import json, random, collections, math
d=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','liber-primus__explorer','data','lp.json')))
GP="ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
PR=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
V={r:PR[i] for i,r in enumerate(GP)}
# words (same rules as workbench), per segment, in order
segs=collections.defaultdict(list); cur=None; prev=None
for p in d['pages']:
    for l in p['lines']:
        key=(l['s'],l['p'])
        if key!=prev: cur=None
        prev=key
        for t in l['t']:
            if t[0] in '-.': cur=None; continue
            if t[0]!='r': cur=None; continue
            if cur is None: cur=[]; segs[l['s']].append(cur)
            cur.append(t[1])
UNS=range(7,16); ENC=(0,1,3,5,16); PLAIN=(2,4,6,17)
def doublets(seglist):
    w_in=w_n=b_in=b_n=0; runes=[]
    for s in seglist:
        ws=segs[s]
        for i,w in enumerate(ws):
            for a,b in zip(w,w[1:]): w_n+=1; w_in+=a==b
            if i+1<len(ws): b_n+=1; b_in+=w[-1]==ws[i+1][0]
            runes+=w
    f=collections.Counter(runes); n=len(runes)
    exp=sum((c/n)**2 for c in f.values())
    return w_in,w_n,b_in,b_n,exp,n
for name,sl in (('unsolved',UNS),('solved-encrypted',ENC),('plaintext',PLAIN)):
    w_in,w_n,b_in,b_n,exp,n=doublets(sl)
    print(f"{name:17s} runes {n:5d} | within-word doublets {w_in}/{w_n} = {w_in/w_n:.4f} | across word gap {b_in}/{b_n} = {b_in/b_n:.4f} | expected if independent {exp:.4f}")
print('---')
words=[w for s in UNS for w in segs[s]]
allr=[r for w in words for r in w]
freq=collections.Counter(allr); n=len(allr)
vals=[V[r] for r in allr]
sums=[sum(V[r] for r in w) for w in words]
print('unsolved words',len(words),'length dist',sorted(collections.Counter(len(w) for w in words).items())[:15])
# exact null distribution of sum for length L under independent runes with observed frequencies
pmf1=collections.Counter()
for r,c in freq.items(): pmf1[V[r]]+=c/n
dists={1:dict(pmf1)}
def dist(L):
    if L in dists: return dists[L]
    a=dist(L-1); out=collections.defaultdict(float)
    for x,px in a.items():
        for y,py in pmf1.items(): out[x+y]+=px*py
    dists[L]=dict(out); return dists[L]
# PIT (randomised) -> should be uniform if sums behave like random-rune sums
pits=[]
for w,s in zip(words,sums):
    D=dist(len(w)); below=sum(p for x,p in D.items() if x<s); at=D.get(s,0)
    pits.append(below+random.random()*at)
bins=[0]*10
for u in pits: bins[min(9,int(u*10))]+=1
expc=len(pits)/10
chi=sum((b-expc)**2/expc for b in bins)
print('PIT deciles',bins,'chi2(9 df)=%.1f  (5%% cutoff 16.9)'%chi)
# set membership tests vs null (shuffle runes across words, keep lengths)
def isp(m):
    if m<2: return False
    for k in range(2,int(m**.5)+1):
        if m%k==0: return False
    return True
fib=[1,2]
while fib[-1]<10**5: fib.append(fib[-1]+fib[-2])
SQ=[2,3,5,7,13,23,43,79,149,263,463,829]
SQRAW={3258,3222,3152,3038,3278,3299,3298,2838,3288,3294,3296,2472,4516,1206,708,1820}
tests={'prime':isp,'fibonacci':lambda x:x in set(fib),'fib prime':lambda x:x in {f for f in fib if isp(f)},
 'square-primes (3301-x)':lambda x:x in set(SQ),'square raw numbers':lambda x:x in SQRAW,
 'perfect square':lambda x:int(x**.5)**2==x,'emirp':lambda x:isp(x) and isp(int(str(x)[::-1])) and str(x)!=str(x)[::-1]}
lens=[len(w) for w in words]
null={k:[] for k in tests}
a=allr[:]
for _ in range(300):
    random.shuffle(a); i=0; ss=[]
    for L in lens: ss.append(sum(V[r] for r in a[i:i+L])); i+=L
    for k,f in tests.items(): null[k].append(sum(map(f,ss)))
for k,f in tests.items():
    obs=sum(map(f,sums)); m=sum(null[k])/len(null[k]); sd=(sum((x-m)**2 for x in null[k])/len(null[k]))**.5
    print(f'{k:24s} observed {obs:5d} ({obs/len(sums):.1%})  shuffled {m:7.1f} ± {sd:5.1f}  z={(obs-m)/(sd or 1):+.2f}')
# Fibonacci-type recurrences between nearby words, mod 3301, allowing chaff to skip real words (gaps 1..3)
hits=0;tot=0
for g in (1,2,3):
    h=sum((sums[i-2*g]+sums[i-g]-sums[i])%3301==0 for i in range(2*g,len(sums))); t=len(sums)-2*g
    print(f'sum[i] = sum[i-{g}] + sum[i-{2*g}] (mod 3301): {h}/{t}')
print('--- recurrence null')
a=allr[:]; res={1:[],2:[],3:[]}
for _ in range(300):
    random.shuffle(a); i=0; ss=[]
    for L in lens: ss.append(sum(V[r] for r in a[i:i+L])); i+=L
    for g in (1,2,3): res[g].append(sum((ss[i-2*g]+ss[i-g]-ss[i])%3301==0 for i in range(2*g,len(ss))))
for g in (1,2,3):
    m=sum(res[g])/300; print(g,'shuffled mean %.1f'%m,'p(>=obs)=%.2f'%(sum(x>=[6,2,3][g-1] for x in res[g])/300))
