import re
import sys
import json
import time
import requests
from bs4 import BeautifulSoup as bs

method = 'GET'
url = 'http://wx.sogou.com/weixin?type=1&query=hit_hica&ie=utf8&_sug_=n&_sug_type_='
headers = {'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0', 'Host': 'wx.sogou.com', 'Referer': 'http://wx.sogou.com/', 'Upgrade-Insecure-Requests': '1'}
res = requests.request(url=url,method=method,headers=headers)

link = re.findall("(?<=main_toweixin_account_name_0.{8}).*?(?=\">)",res.text)
link = sys.exit(-1) if link==[] else link[0].replace('amp;','')
updateTime = re.findall("(?<=timeConvert.{2}).*?(?='\))",res.text)
updateTime = sys.exit(-2) if updateTime==[] else time.strftime("%Y-%m-%d", time.localtime(int(updateTime[0])))

#do we need to update?
with open('index/index.json', 'r') as f:
	oldList = json.load(f)
if oldList['msgList'][-1]['id'][:-2] == updateTime:
	sys.exit(-3)

#using the same  method
url = link
headers = {'Accept-Language': 'en-US,en;q=0.5', 'Accept-Encoding': 'gzip, deflate', 'Connection': 'keep-alive', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:50.0) Gecko/20100101 Firefox/50.0', 'Host': 'mp.weixin.qq.com', 'Cache-Control': 'max-age=0', 'Upgrade-Insecure-Requests': '1'}
res = requests.request(url=url,method=method,headers=headers)

msg = re.findall("(?<=msgList.{3}).*(?=.{2})",res.text)
msg = sys.exit(-4) if msg==[] else json.loads(msg[0])

getUrl = lambda msgInfo: "http://mp.weixin.qq.com"+msgInfo['content_url'].replace('amp;','')
getMsg = lambda msgInfo,id: {'author':msgInfo['author'],'cover':msgInfo['cover'],'digest':msgInfo['digest'],'id':id, 'title':msgInfo['title'],'source_url':msgInfo['source_url']}

index = 0 #latest news
rawMsgs = msg['list'][index]['app_msg_ext_info']
date = time.strftime("%Y-%m-%d", time.localtime(msg['list'][index]['comm_msg_info']['datetime']))
urlList = [getUrl(rawMsgs)]
msgList = [getMsg(rawMsgs,date+'-0')]
if rawMsgs['is_multi'] == 1:
	multiList = rawMsgs['multi_app_msg_item_list']
	urlList += [getUrl(item) for item in multiList]
	msgList += [getMsg(multiList[i],date+'-'+str(i+1)) for i in xrange(len(multiList))]
	
for i in xrange(len(urlList)):
	#using the same method
	url = urlList[i]
	#using the same  headers
	res = requests.request(url=url,method=method,headers=headers)
	
	soup = bs(res.text,'lxml')
	content = soup.find_all(id="js_content")
	content = sys.exit(-5) if content==[] else content[0].prettify().replace('data-src','src')
	with open('articles/'+str(msgList[i]['id']),'w') as f:
		f.write(content.encode('utf-8'))
	time.sleep(30)

msgList = oldList['msgList'] + msgList
if len(msgList) > 50:
	with open('index/'+msgList[50]['id']+'.json', 'w') as f:
		json.dump({'msgList':msgList[:50]}, f)
	msgList = msgList[50:]
with open('index/index.json', 'w') as f:
	json.dump({'msgList':msgList}, f)