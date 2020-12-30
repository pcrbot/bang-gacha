import os
import re
import requests
import calendar

from bs4 import BeautifulSoup

#config
download_pic=True
pool_range=range(0,160)


pooldict ={}

pool_dir = 'bdpool/'
os.makedirs(pool_dir, exist_ok=True)

headers={"accept-language": "ja"}

for id in pool_range:

    try:
        res=requests.get(f"https://bandori.party/gachas/{id}",headers=headers)
        if res.status_code==404:
            print(f"pool {id} dont exist")
            continue
        soup = BeautifulSoup(res.text, features="lxml")

        poolid = id

        name = soup.find(string='タイトル').parent.parent.next_sibling.next_sibling.text
        name = name.replace("  ","").replace("\n","").replace("\t","").replace("Gacha","ガチャ")
        
        pooltype = soup.find(string='ガチャタイプ').parent.parent.next_sibling.next_sibling.text
        pooltype = pooltype.replace("  ","").replace("\n","").replace("\t","")
        if pooltype=="ドリームフェスティバル":
            print(f"pool {poolid} is a Fes pool, uplist might be imcomplete.")

        time = soup.findAll(attrs={'data-to-timezone':'Asia/Tokyo'})

        start = time[0].find(attrs={'class':'datetime'}).text
        month=re.match("(\w*)\s(\d*)\,\s(\d*)\s", start).group(1)
        day=re.match("(\w*)\s(\d*)\,\s(\d*)\s", start).group(2)
        year=re.match("(\w*)\s(\d*)\,\s(\d*)\s", start).group(3)
        month=list(calendar.month_name).index(month)
        start =f"{year}/{month}/{day}"

        end = time[1].find(attrs={'class':'datetime'}).text
        month=re.match("(\w*)\s(\d*)\,\s(\d*)\s", end).group(1)
        day=re.match("(\w*)\s(\d*)\,\s(\d*)\s", end).group(2)
        year=re.match("(\w*)\s(\d*)\,\s(\d*)\s", end).group(3)
        month=list(calendar.month_name).index(month)
        end =f"{year}/{month}/{day}"
        
        upcard = soup.find(attrs={'data-field':'cards'})
        cardlist = re.finditer(r"/ajax/card/(\d*)/", str(upcard))
        uplist = []
        for i in cardlist:
            uplist.append(i.group(1))
        
        pooldict[id]=[name,pooltype,start, end, uplist]

        if download_pic:
            image = soup.find(string='日本のサーバー').parent.parent.parent.a["href"]
            png_path = os.path.join(pool_dir,  f"{id}.png")
            if not os.path.exists(png_path):
                png = requests.get(f"http:{image}", timeout=20).content
                with open(png_path, 'wb') as f:
                    f.write(png)
        
        if not id % 10:
            print(f"added {id}")
            
    except Exception as e:
        print(f"error downloading id={id}")
        print(e)
        continue

with open('bang_pool.csv', 'w', encoding='utf-8-sig') as f:
    f.write("id,name,type,start,end,up1,up2,up3\n")
    for item in pooldict:
        f.write(f"{item},")
        for attri in pooldict[item]:
            if type(attri)==list:
                for up in attri:
                    f.write(f"{up},")
            else:
                f.write(f"{attri},")
        f.write("\n")
