import json,sys,os
sys.path.insert(0,'/home/user/iddqd/liber-primus__analysis')
VAL=[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,103,107,109]
def ct():
    return json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','ciphertext.json')))['clauses']
def uns():
    from lp_common import UNS
    cls=[];lastc=lastw=None
    for r in UNS:
        if r['clause']!=lastc: cls.append([]); lastc=r['clause']; lastw=None
        if r['word']!=lastw: cls[-1].append([]); lastw=r['word']
        cls[-1][-1].append(r['c'])
    return cls
