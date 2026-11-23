import os,sys,numpy as np
H='/home/user/iddqd/liber-primus__analysis'
src=open(H+'/full_model_harness.py').read().split('# ---------------- self-test')[0]
__file__=H+'/full_model_harness.py'
exec(src)
S='/tmp/claude-0/-home-user-iddqd/c4d0f226-87a8-5085-be90-4aec3e9a339e/scratchpad/iso/'
N=20000
def conv(b,mode):
    b=b.astype(int)
    if mode=='raw': return b[:N]
    if mode=='rej29':
        b=b[b<232]%29; return b[:N]
    if mode=='rej28':
        b=b[b<252]%28; return b[:N]
res=[]
rng=np.random.default_rng(1)
for name,start in [('_560.00',0),('560.17',0),('560.13',0),('560.13',64167),('560.13',12821+23),('560.13',20709)]:
    a=np.fromfile(S+name,np.uint8)[start:start+200000]
    for mode in ['raw','rej29','rej28']:
        K=conv(a,mode)
        b=scan(K,offsets=range(0,400),restarts=('none','segment'))
        res.append((round(b[0],4),name,start,mode,b[1])); print(res[-1],flush=True)
ctl=[scan(rng.integers(0,256,N),offsets=range(0,400))[0] for _ in range(3)]
print('random controls',ctl)
