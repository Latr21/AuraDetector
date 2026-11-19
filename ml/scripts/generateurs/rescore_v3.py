import csv, random
from collections import Counter
R = random.Random(7)
W = dict(R=0.30/0.9, S=0.20/0.9, O=0.15/0.9, B=0.15/0.9, P=0.10/0.9)
C = [('Anti-Aura',-100,-41),('Aura Faible',-40,-11),('Aura Neutre',-10,4),('Aura Correcte',5,24),('Forte Aura',25,49),('Aura Légendaire',50,74),('Aura Divine',75,100)]
OFF = {"brainrot": dict(R=5,S=0,O=18,B=-8,P=-12), "politique": dict(R=5,S=15,O=-10,B=5,P=-5),
       "moderne": dict(R=10,S=-3,O=0,B=-5,P=-12), "prose": dict(R=-10,S=-8,O=-5,B=18,P=18),
       "hybride": dict(R=0,S=0,O=15,B=5,P=10)}
def cl(s): return next(n for n,a,b in C if a<=s<=b)
def score(x): return round(sum(int(x[k])*w for k,w in W.items()))
rows = list(csv.DictReader(open('aura_dataset_v2.csv', encoding='utf-8-sig')))
fixed = 0
for x in rows:
    x.pop('M')
    if cl(score(x)) != x['classe']:
        lo, hi = next((a,b) for n,a,b in C if n == x['classe'])
        while True:
            t = R.uniform(lo, hi)
            comp = {k: max(-100, min(100, round(t + OFF[x['style']][k] + R.gauss(0, 9)))) for k in W}
            if cl(round(sum(comp[k]*W[k] for k in W))) == x['classe']: break
        x.update({k: str(v) for k, v in comp.items()}); fixed += 1
    x['score'] = score(x)
cols = ["texte","classe","score","justification","style","R","S","O","B","P"]
with open('aura_dataset_v3.csv','w',newline='',encoding='utf-8-sig') as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
print(fixed, Counter(x['classe'] for x in rows))
print(all(cl(x['score'])==x['classe'] for x in rows))
