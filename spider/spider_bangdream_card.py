import os
import re
import requests
import calendar

from bs4 import BeautifulSoup

#config
download_icon=True
card_range=range(500,1600)


chlist={"CHU²":"チュチュ",
"PAREO":"パレオ",
"MASKING":"マスキング",
"LAYER":"レイヤ",
"LOCK":"ロック",
"Misaki Okusawa":"奥沢美咲",
"Rui Yashio":"八潮瑠唯",
"Rinko Shirokane":"白金燐子",
"Chisato Shirasagi":"白鷺千聖",
"Hagumi Kitazawa":"北沢はぐみ",
"Hina Hikawa":"氷川日菜",
"Sayo Hikawa":"氷川紗夜",
"Mashiro Kurata":"倉田ましろ",
"Yukina Minato":"湊友希那",
"Maya Yamato":"大和麻弥",
"Tsukushi Futaba":"二葉つくし",
"Nanami Hiromachi":"広町七深",
"Kasumi Toyama":"戸山香澄",
"Tae Hanazono":"花園たえ",
"Lisa Imai":"今井リサ",
"Kaoru Seta":"瀬田薫",
"Ran Mitake":"美竹蘭",
"Rimi Ushigome":"牛込りみ",
"Moca Aoba":"青葉モカ",
"Eve Wakamiya":"若宮イヴ",
"Saaya Yamabuki":"山吹沙綾",
"Himari Uehara":"上原ひまり",
"Arisa Ichigaya":"市ヶ谷有咲",
"Kanon Matsubara":"松原花音",
"Touko Kirigaya":"桐ヶ谷透子",
"Aya Maruyama":"丸山彩",
"Kokoro Tsurumaki":"弦巻こころ",
"Ako Udagawa":"宇田川あこ",
"Tomoe Udagawa":"宇田川巴",
"Tsugumi Hazawa":"羽沢つぐみ"}

res=requests.get("https://appmedia.jp/bang_dream/5004943")
soup = BeautifulSoup(res.text, features="lxml")

cardappmedia=soup.findAll(attrs={'class':'result_tr_td'})

appmediadict ={}
namelist =[]

k=0

for card in cardappmedia:
    cid=k;
    name=card['data-card_name']
    chara=card['data-chara']
    color=card['data-type']
    star=card['data-rarity']
    skill=card['data-skill_text']
    get=card['data-get']
    appmediadict[cid]=[name,chara,color,star,skill,get]
    namec=name+chara
    namelist.append(namec)
    k+=1

print("appmedia data loaded.")

carddict ={}

icon_dir = 'bdicon/'
os.makedirs(icon_dir, exist_ok=True)

for id in card_range:
    try:
        res=requests.get(f"https://bandori.party/cards/{id}")
        if res.status_code==404:
            print(f"card {id} do not exist")
            continue
        soup = BeautifulSoup(res.text, features="lxml")

        cardid = id

        try:
            name = soup.find(attrs={'data-field':'card_name'}).p.text
        except AttributeError:
            name = soup.find(string='Title').parent.parent.next_sibling.next_sibling.text
            name = name.replace(" ","").replace("\n","").replace("\t","")
        
        chara = soup.find(attrs={'class':'member-name'}).text
        if chara in chlist:
            chara_jp = chlist[chara]
            
        rarity = len(soup.find(attrs={'data-field':'rarity'}).findAll("img"))

        color = soup.find(string='Attribute').parent.parent.next_sibling.next_sibling.text
        color = color.replace(" ","").replace("\n","").replace("\t","")
        
        namec = name + chara_jp
        if namec in namelist:
            get = appmediadict[namelist.index(namec)][5]
        elif rarity==1:
            get = "初期カード"
        else:
            get = "unknown"
            print(f"error checking appmedia data for card {id}, please check manually.")

        date = soup.find(attrs={'class':'datetime'}).text
        month=re.match("(\w*)\s(\d*)\,\s(\d*)\s", date).group(1)
        day=re.match("(\w*)\s(\d*)\,\s(\d*)\s", date).group(2)
        year=re.match("(\w*)\s(\d*)\,\s(\d*)\s", date).group(3)
        month=list(calendar.month_name).index(month)
        date =f"{year}/{month}/{day}"
        
        try:
            skillname = soup.find(attrs={'data-field':'skill_name'}).p.text
        except AttributeError:
            skillname = soup.find(string='Skill name').parent.parent.next_sibling.next_sibling.text
            skillname = skillname.replace(" ","").replace("\n","").replace("\t","")
        
        skilltype = soup.find(attrs={'data-field':'japanese_skill'}).strong.text
        skilldiscribe = soup.find(attrs={'data-field':'japanese_skill'}).p.text

        if download_icon:
            iconlist=soup.findAll(alt='Icon')
            st=0
            for icon in iconlist:
                png = requests.get(f"http:{icon['src']}", timeout=20).content
                png_path = os.path.join(icon_dir, f"{cardid}_{st}.png")
                if os.path.exists(png_path):
                    continue
                st+=1
                with open(png_path, 'wb') as f:
                    f.write(png)
        
        carddict[id]=[name,chara,chara_jp,color,rarity,date,get,skillname,skilltype,skilldiscribe]
        
        if not id % 10:
            print(f"added {id}")
    except Exception as e:
        print(f"error downloading id={id}")
        print(e)
        continue

with open('bang_party.csv', 'w', encoding='utf-8-sig') as f:
    f.write("id,name,chara,chara_jp,color,rarity,date,get,skillname,skilltype,skilldiscribe\n")
    for item in carddict:
        f.write(f"{item},")
        for attri in carddict[item]:
            f.write(f"{attri},")
        f.write("\n")
