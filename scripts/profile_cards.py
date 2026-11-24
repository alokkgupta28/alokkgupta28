import os,json,urllib.request,collections,html
from pathlib import Path
u=os.environ['GITHUB_REPOSITORY_OWNER']
token=os.environ['GH_TOKEN']
def api(url, data=None):
    req=urllib.request.Request(url, data=json.dumps(data).encode() if data else None, headers={'Authorization':'Bearer '+token,'User-Agent':'profile-cards','Content-Type':'application/json'})
    return json.load(urllib.request.urlopen(req))
q='''query($u:String!){user(login:$u){followers{totalCount} repositories(first:100,ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC){totalCount nodes{stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}} contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{contributionCount}}}}}}'''
result=api('https://api.github.com/graphql',{'query':q,'variables':{'u':u}})
d=result['data']['user']
repos=d['repositories']; stars=sum(r['stargazerCount'] for r in repos['nodes']); followers=d['followers']['totalCount']; cal=d['contributionsCollection']['contributionCalendar']; langs=collections.Counter()
for r in repos['nodes']:
    for e in r['languages']['edges']: langs[e['node']['name']]+=e['size']
out=Path('cards');out.mkdir(exist_ok=True)
def txt(x,y,s,size=13,color='#c5d5e8',bold=False):
    return f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{700 if bold else 400}" font-family="Arial,sans-serif">{html.escape(str(s))}</text>'
def card(name,title,h,body):
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" width="720" height="{h}" viewBox="0 0 720 {h}"><defs><linearGradient id="g" x2="1" y2="1"><stop stop-color="#152c45"/><stop offset=".45" stop-color="#10171e"/><stop offset=".75" stop-color="#20352f"/><stop offset="1" stop-color="#153b50"/></linearGradient><radialGradient id="a"><stop stop-color="#376eaa" stop-opacity=".45"/><stop offset="1" stop-color="#376eaa" stop-opacity="0"/></radialGradient></defs><rect x="1" y="1" width="718" height="{h-2}" rx="24" fill="url(#g)" stroke="#344b60"/><ellipse cx="120" cy="12" rx="190" ry="65" fill="url(#a)"/><rect x="16" y="16" width="688" height="{h-32}" rx="15" fill="#0b1119" fill-opacity=".78" stroke="#405268"/>{txt(32,44,title,20,'#edf5ff',True)}{body}</svg>'''
    (out/(name+'.svg')).write_text(svg)
def tiles(items):
    b=''
    for i,(label,val) in enumerate(items):
        w=640/len(items);x=32+i*w
        b+=f'<rect x="{x}" y="62" width="{w-10}" height="65" rx="9" fill="#111c29" stroke="#35465c"/>'+txt(x+10,82,label,11)+txt(x+10,112,val,23,'#7dcfff',True)
    return b
card('signal','Profile Signal',150,tiles([('Stars',stars),('Contributions',cal['totalContributions']),('Repositories',repos['totalCount']),('Followers',followers)]))
body='';total=sum(langs.values()) or 1
for i,(name,n) in enumerate(langs.most_common(5)):
    y=78+i*27;p=n/total*100;c=['#66aaff','#64b6df','#e9b44c','#a99be9','#e6d45a'][i]
    body+=txt(32,y,name,13)+txt(190,y,f'{p:.1f}%',12,c)+f'<rect x="250" y="{y-10}" width="420" height="8" rx="4" fill="#263441"/><rect x="250" y="{y-10}" width="{420*p/100}" height="8" rx="4" fill="{c}"/>'
card('stack','Language Stack',220,body)
card('highlights','Highlights',150,tiles([('Open Source',str(repos['totalCount'])+' repos'),('Impact',str(stars)+' stars'),('Community',str(followers)+' followers')]))
body=txt(32,64,str(cal['totalContributions'])+' contributions in the last year',12)
for i,w in enumerate(cal['weeks']):
    for j,day in enumerate(w['contributionDays']):
        n=day['contributionCount'];c=['#1c2935','#244766','#32658e','#458bc2','#7dcfff'][0 if n==0 else min(4,1+(n-1)//3)]
        body+=f'<rect x="{32+i*12.3}" y="{78+j*12}" width="10" height="10" rx="2" fill="{c}"/>'
card('activity','Contribution Activity',180,body)
