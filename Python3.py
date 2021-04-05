import requests
from bs4 import BeautifulSoup
import operator
from datetime import timedelta,date



def dictionary(allwords): #kelime frekanslarını hesaplamak için
    wordcount = {}
    for word in allwords:
        if word in wordcount:
            wordcount[word] +=1
        else:
            wordcount[word] = 1

    for key, value in sorted(wordcount.items(), reverse=True, key=operator.itemgetter(1)):
        print(key, ":", value)

    return wordcount



def clearsymbols(allwords): #sembolleri temizlemek için
    symbollesswords = []
    symbols = "!'^+%&/?*-_{}[]#$""<<>.,'';:/=()0123456789"  + chr(34)
    for word in allwords:
        for symbol in symbols:
            if symbol in word:
                word = word.replace(symbol,"")
        if(len(word) > 0):
             symbollesswords.append(word)
    return symbollesswords


def isPaging(soup):# Haber içeriği sayfalardan mı oluşuyor
    paging = soup.findAll("div", {"class": "paging"})
    if paging == []:
        return False,1
    number_of_pages = len(paging[0].findAll('li'))-2 # paging kısmına baktım <li> elementlerinin 2 tanesi dışındakiler sayfa elementleri
    return True,number_of_pages



def fetchNews(category,date):
    url= "https://www.sabah.com.tr/timeline/{}?c={}".format(date,category)
    web_site = "https://www.sabah.com.tr"
    r = requests.get(url)
    soup = BeautifulSoup(r.content,"html.parser")
    divs = soup.findAll("div", {"class": "innerItem"}) # tüm haber başlıklarının tutulduğu kısım
    news_url = ''#İlgili haberin içeriğinin yer aldığı url i
    news = [] # haberlerin içerikleri
    for div in divs:
        try:
            sub_url = div.find('a')['href']
            if sub_url[0:4] != 'http':#bazı durumlarda sub url https şeklinde web site adresi eklenmiş şekilde geliyor. Default -> /ekonomi/2020/02/15 ile başlaması.
                news_url = web_site + sub_url # sub url(/ekonomi/..) https şekline dönüştürüldü.
            elif 'galeri' in sub_url:#galeri içeren urlleri es geç
                continue
            else:# dönüştürme işlemşne gerek kalmayan sub url
                news_url = sub_url
            r = requests.get(news_url)
            soup = BeautifulSoup(r.content,"html.parser")
            flag,value = isPaging(soup)
            #print(flag,value)
            if flag: # haberde sayfalama var mı?
                new = soup.findAll("div", {"class": "newsBox"})[0].findAll('p')
                for i in range(2,value+1): # ilk sayfayı yukarda aldık 2 den başlıyoruz
                    r = requests.get(news_url+"?paging="+str(i)) # diğer sayfalara istek atıyoruz  web sitesi ?paging= ile yapıyor bunu
                    soup = BeautifulSoup(r.content,"html.parser")
                    new_paging = soup.findAll("div", {"class": "newsBox"})[0].findAll('p')
                    new += new_paging # yeni sayfadaki haberi 1. sayfadakiyle birleştirdik
                news.append(new)
            else:
                news.append(soup.findAll("div", {"class": "newsBox"})[0].findAll('p'))
        except:
            continue
    return news


def daterange(date1, date2):
    for n in range(int ((date2 - date1).days)+1):
        yield date1 + timedelta(n)


dateRange = []
print("Enter start date->")
start_dt = date(int(input('Enter a year:')), int(input('Enter a month:')), int(input('Enter a day:')))
print("Enter end date->")
end_dt = date(int(input('Enter a year:')), int(input('Enter a month:')), int(input('Enter a day:')))
for dt in daterange(start_dt, end_dt):
    dateRange.append(str(dt).replace('-','/'))


categories = ['gundem','ekonomi','yasam','dunya']#medya,spor


allwords = []
for date in dateRange:
    for category in categories:
        #print(category)
        news = fetchNews(category,date)
        for i in range(0,len(news)): # Haberler
            for j in range(0,len(news[i])):# Her haberin paragrafları
                #print(news[i][j].text)
                content = news[i][j].text
                words = content.lower().split()
                #print(words)
                for word in words:
                    allwords.append(word)



file = open("python.txt","w")
allwords = clearsymbols(allwords)
wordcount = dictionary(allwords)

for key, value in sorted(wordcount.items(), reverse=True, key=operator.itemgetter(1)):
    line = key + ":" + str(value)+" "
    file.writelines(line)
file.close()