# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 23:00:28 2018
@author: wangshuai
"""
import urllib
import urllib.request as urllib2
import time
import http.cookiejar as cookielib
import io
import os
import sys
import gzip
import lxml.html
from selenium import webdriver
from opencc import OpenCC
import warnings
warnings.filterwarnings("ignore")
import datetime
def getYesterday(): 
    today=datetime.date.today() 
    oneday=datetime.timedelta(days=1) 
    yesterday=today-oneday  
    return yesterday
class Config:
    def __init__(self):
        self.config = {}
        self.config["headers"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36"
        self.config["outputPath"] = "./"
        self.config["url_TW_T"] = "https://tw.news.appledaily.com/politics/realtime"
        self.config["url_TW_Y"] = "https://tw.news.appledaily.com/politics/realtime/2"
        self.config["url_HK_T"] = "https://news.mingpao.com/pns/%E6%B8%AF%E8%81%9E/web_tc/section/"+time.strftime("%Y%m%d")+"/s00002"
        self.config["url_HK_Y"] = "https://news.mingpao.com/pns/%E6%B8%AF%E8%81%9E/web_tc/section/"+str(getYesterday()).replace("-","")+"/s00002"    
        self.config["url_HK_T_YW"] = "https://news.mingpao.com/pns/%E8%A6%81%E8%81%9E/web_tc/section/"+time.strftime("%Y%m%d")+"/s00001"
        self.config["url_HK_Y_YW"] = "https://news.mingpao.com/pns/%E6%B8%AF%E8%81%9E/web_tc/section/"+str(getYesterday()).replace("-","")+"/s00001"        
    def get(self, key, parent=None):
        if key and key in self.config.keys():
            return self.config[key]
def get_Html(url, js = False, time = 0):
    config = Config()
    if js:
        try:
            driver = webdriver.PhantomJS()
            driver.get(url)
        except Exception as err:
            print (err)
            print ("=== 网络不稳定，再次连接 ...")    
            if time==0:
                return -1
            time -= 1
            return get_Html(url, js=True, time=time)
        html = driver.page_source
        driver.close()
        return html
    else:        
        try:
            cj = cookielib.CookieJar()
            proxy = urllib2.ProxyHandler({'https': '127.0.0.1:1080'})
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            opener.addheaders = [("User-agent", config.get("headers"))]
            urllib2.install_opener(opener)
            req=urllib2.Request(url)
            con=urllib2.urlopen(req)
            html=con.read()
            if con.getheader('Content-Encoding') == "gzip":
                buf = io.BytesIO(html) 
                gf = gzip.GzipFile(fileobj=buf)
                html = gf.read()
            html = html.decode('utf-8')
        except Exception as err:
            print (err)
            print ("=== 网络不稳定，再次连接 ...")   
            if time==0:
                return -1
            time -= 1
            return get_Html(url, js=False, time=time)
        return html
def save(info, url_flag, dir_path):
    if url_flag == "TW_T" or url_flag == "TW_Y":
        openCC = OpenCC('tw2sp')
    elif url_flag == "HK_T" or url_flag == "HK_Y":
        openCC = OpenCC('hk2s')
    filename = openCC.convert(info[url_flag]["title"])+".txt"
    outfile = open(dir_path+"/"+filename,"w",encoding='utf-8')
    for ss in ["title","url","detail"]:
        txt = info[url_flag][ss].strip(" ")
        txt_converted = openCC.convert(txt)
        outfile.write(txt_converted+"\r\n")                  
    outfile.close()
class GetList:
    def __init__(self, config):
        self.config = config
        self.articleList = {}
        self.url_TW_T = self.config.get("url_TW_T")
        self.url_HK_T = self.config.get("url_HK_T")
        self.url_HK_T_YW = self.config.get("url_HK_T_YW")
        
        self.url_TW_Y = self.config.get("url_TW_Y")
        self.url_HK_Y = self.config.get("url_HK_Y")
        self.url_HK_Y_YW = self.config.get("url_HK_Y_YW")
        
    def index(self): 
        tree_TW_T = lxml.html.fromstring(get_Html(self.url_TW_T, js=False, time=3))
        tree_HK_T = lxml.html.fromstring(get_Html(self.url_HK_T, js=True, time=3))
        tree_HK_T_YW = lxml.html.fromstring(get_Html(self.url_HK_T_YW, js=True, time=3))
        
        tree_TW_Y = lxml.html.fromstring(get_Html(self.url_TW_Y, js=False, time=3))
        tree_HK_Y = lxml.html.fromstring(get_Html(self.url_HK_Y, js=True, time=3))        
        tree_HK_Y_YW = lxml.html.fromstring(get_Html(self.url_HK_Y_YW, js=True, time=3))        
        
        select_TW_T = tree_TW_T.cssselect('#maincontent > div.thoracis > div.abdominis.rlby.clearmen > ul:nth-child(2) > li > a')
        select_HK_T = tree_HK_T.cssselect('#blocklisting2 > div > ul')
        select_HK_T_YW_1 = tree_HK_T_YW.cssselect('#blocklisting1 > div.headline > div.right > a')        
        select_HK_T_YW_2 = tree_HK_T_YW.cssselect('#blocklisting2 > div.listing > ul > li > a')        

        select_TW_Y_1 = tree_TW_T.cssselect('#maincontent > div.thoracis > div.abdominis.rlby.clearmen > ul:nth-child(4) > li > a')
        select_TW_Y_2 = tree_TW_Y.cssselect('#maincontent > div.thoracis > div.abdominis.rlby.clearmen > ul:nth-child(2) > li > a')                
        select_TW_Y_3 = tree_TW_Y.cssselect('#maincontent > div.thoracis > div.abdominis.rlby.clearmen > ul:nth-child(4) > li > a')                
        count_TW_Y = tree_TW_Y.cssselect('#maincontent > div.thoracis > div.abdominis.rlby.clearmen > h1')                      
        select_HK_Y = tree_HK_Y.cssselect('#blocklisting2 > div > ul')        
        select_HK_Y_YW_1 = tree_HK_Y_YW.cssselect('#blocklisting1 > div.headline > div.right > a')        
        select_HK_Y_YW_2 = tree_HK_Y_YW.cssselect('#blocklisting2 > div.listing > ul > li > a')        
        
        self.articleList["TW_T"] = [select_TW_T[i].get('href') for i in range(len(select_TW_T))]
        self.articleList["HK_T"] = []
        self.articleList["HK_T"].append(select_HK_T_YW_1[0].get('href'))
        for i in range(len(select_HK_T_YW_2)):
            self.articleList["HK_T"].append(select_HK_T_YW_2[i].get('href'))
        for j in range(len(select_HK_T)):
            self.articleList["HK_T"].append(select_HK_T[j].cssselect("li > a")[0].get('href'))        

        self.articleList["TW_Y"] = []
        if len(select_TW_Y_1):
            for i in range(len(select_TW_Y_1)):
                self.articleList["TW_Y"].append(select_TW_Y_1[i].get('href'))
        if len(count_TW_Y)==2:
            for k in range(len(select_TW_Y_3)):
                self.articleList["TW_Y"].append(select_TW_Y_3[k].get('href'))
        elif len(count_TW_Y)==1:
            for j in range(len(select_TW_Y_2)):
                self.articleList["TW_Y"].append(select_TW_Y_2[j].get('href'))                            
        self.articleList["HK_Y"] = []
        self.articleList["HK_Y"].append(select_HK_Y_YW_1[0].get('href'))
        for i in range(len(select_HK_Y_YW_2)):
            self.articleList["HK_Y"].append(select_HK_Y_YW_2[i].get('href'))
        for j in range(len(select_HK_Y)):
            self.articleList["HK_Y"].append(select_HK_Y[j].cssselect("li > a")[0].get('href'))
        return self.articleList    
class GetArticles:
    def __init__(self, config, getlist):
        self.getlist = getlist
        self.config = config
        self.articleList = self.getlist.index()
        self.articleDetail = {}
        self.articleDetail["TW_T"] = {}
        self.articleDetail["HK_T"] = {}
        self.articleDetail["TW_Y"] = {}
        self.articleDetail["HK_Y"] = {}
    def article_TW(self, url_flag=''):
        if url_flag == "TW_T":
            dir_path = './'+time.strftime("%Y-%m-%d")+'/'+time.strftime("%Y-%m-%d")+"-苹果日报"
        elif url_flag == "TW_Y":
            dir_path = './'+str(getYesterday())+'/'+str(getYesterday())+"-苹果日报"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for i, url in enumerate(self.articleList[url_flag]):
            try:
                link_TW = urllib.parse.urljoin(self.getlist.url_TW_T if url_flag == "TW_T" else self.getlist.url_TW_Y, url)
                print ("TW-"+str(i+1)+": "+link_TW)
                tree_TW = lxml.html.fromstring(get_Html(link_TW, js=False, time=3))
                title_TW = tree_TW.cssselect("#article > div.wrapper > div > main > article > hgroup > h1")
                openCC = OpenCC('tw2sp')
                filename = openCC.convert(title_TW[0].text_content())+".txt"
                if filename in os.listdir(dir_path):
                    print ("... 第"+str(i+1)+"篇文章已存在 ...")
                    continue
                detail_TW = tree_TW.cssselect("#article > div.wrapper > div > main > article > div.ndArticle_contentBox > article > div > p")
                self.articleDetail[url_flag]["title"] = title_TW[0].text_content()
                self.articleDetail[url_flag]["url"] = link_TW
                if (title_TW and detail_TW):
                    self.articleDetail[url_flag]["detail"] = "【苹果日报】"+detail_TW[0].text_content()
                    rr = self.articleDetail[url_flag]["detail"].find("想知道更多，一定要看") 
                    if rr:
                        self.articleDetail[url_flag]["detail"]=self.articleDetail[url_flag]["detail"].replace(self.articleDetail[url_flag]["detail"][rr:],"")
                else:
                    detail_TW = tree_TW.cssselect("#article > div.wrapper > div > main > article > div > div.ndArticle_contentBox > article > div > p")
                    self.articleDetail[url_flag]["detail"] = "【苹果日报】"+detail_TW[0].text_content()
                    rr = self.articleDetail[url_flag]["detail"].find("想知道更多，一定要看")                    
                    if rr:
                        self.articleDetail[url_flag]["detail"]=self.articleDetail[url_flag]["detail"].replace(self.articleDetail[url_flag]["detail"][rr:],"")
                save(self.articleDetail, url_flag, dir_path)

            except Exception as err:
                print (err)
                print ("... 第"+str(i+1)+"篇文章解析失败 ...")
                continue
    def article_HK(self, url_flag=''):
        if url_flag == "HK_T":
            dir_path = './'+time.strftime("%Y-%m-%d")+'/'+time.strftime("%Y-%m-%d")+"-香港民报"
        elif url_flag == "HK_Y":
            dir_path = './'+str(getYesterday())+'/'+str(getYesterday())+"-香港民报"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path) 
        for i, url in enumerate(self.articleList[url_flag]):
            try:
                link_HK = urllib.parse.urljoin(self.getlist.url_HK_T if url_flag == "HK_T" else self.getlist.url_HK_Y, url)
                print ("HK-"+str(i+1)+": "+link_HK)
                tree_HK = lxml.html.fromstring(get_Html(link_HK, js=True, time=3))
                title_HK = tree_HK.cssselect("#blockcontent > hgroup > h1")
                openCC = OpenCC('hk2s')
                filename = openCC.convert(title_HK[0].text_content())+".txt"
                if filename in os.listdir(dir_path):
                    print ("... 第"+str(i+1)+"篇文章已存在 ...")
                    continue
                detail_HK_upper = tree_HK.cssselect("#upper > p")
                detail_HK_lower = tree_HK.cssselect("#lower > p")
                self.articleDetail[url_flag]["title"] = title_HK[0].text_content()
                self.articleDetail[url_flag]["url"] = link_HK
                if (title_HK and detail_HK_upper and detail_HK_upper):
                    detail_HK = ""
                    detail_HK += detail_HK_upper[0].text_content()+"\r\n"                             
                    for j in range(len(detail_HK_lower)):
                        detail_HK += detail_HK_lower[j].text_content()+"\r\n"                       
                    self.articleDetail[url_flag]["detail"] = detail_HK

                save(self.articleDetail, url_flag, dir_path)

            except Exception as err:
                print (err)
                print ("... 第"+str(i+1)+"篇文章解析失败 ...")
                continue    
   
if __name__ == '__main__':
    config = Config()
    print ("\r\n请输入需要爬取新闻的日期：")
    print ("T: today; \r\nY: yesterday; \r\nA: all")
    S_flag = input()
    print ("=== 正在爬取苹果日报和香港民报，请稍候: ===\r\n")
    getList = GetList(config)
    getArticles = GetArticles(config, getList)
    if not (S_flag == "T" or S_flag == "A" or S_flag == "Y"):
        print ("输入错误，请退出并重新运行程序！\r\n")
        sys.exit(0)
    if S_flag == "T" or S_flag == "A":
        dir_path = './'+time.strftime("%Y-%m-%d")
        if not os.path.exists(dir_path):   
            os.makedirs(dir_path)
        print ("新闻日期为： "+time.strftime("%Y-%m-%d")+"\r\n")
        getArticles.article_TW("TW_T")
        getArticles.article_HK("HK_T")        
    if S_flag == "Y" or S_flag == "A":
        dir_path = './'+str(getYesterday())
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        print ("\r\n"+"新闻日期为： "+str(getYesterday())+"\r\n")
        getArticles.article_TW("TW_Y")
        getArticles.article_HK("HK_Y")
   
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
