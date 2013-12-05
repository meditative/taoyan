#-*- coding: UTF-8 -*- 
'''
Created on 2013-9-29

@author: Tony
'''
import urllib2
import urllib
import cookielib
import os
import re
import threading
import time
import copy

# timeout = 20
semaphore = threading.Semaphore(20)
levelfriendlist = []
renrenUrl = "http://www.renren.com/PLogin.do"
lock = threading.Lock()
level_list = set()
profile = r'http://www.renren.com/%s/profile?v=info_timeline'
album = r'http://photo.renren.com/photo/%s/album/relatives'

class crawler(object):
    def __init__(self, username=None, password = None, url=renrenUrl, friendlist=None):
        self._username = username
        self._password = password
        self._friendlist = friendlist
        self.html = ''
        self.url = url
    
    def login(self):
        try:
            cookJar = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookJar))
            opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
            data = urllib.urlencode({"email":self._username,"password":self._password})
            op = opener.open(self.url, data)
            data= op.read()
            domain = r'http://www.renren.com/'
            pattern = re.compile(domain + '\d+')
            match = pattern.findall(str(data))
            id = str(match[0].replace(domain,''))
            for item in cookJar:
                if item.name == 'societyguester':
                    self._sessionid = item.value
                    self._id = id
                    return True
        except:
            print 'username or password is invalid'
            return False
    
    def getHtml(self, url, ret = []):
        try:
            cookie = 't='+self._sessionid+';'
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookielib.CookieJar()))
            urllib2.install_opener(opener)
            req = urllib2.Request(url)
            req.add_header('Cookie', cookie)
            content = urllib2.urlopen(req).read()#.decode('utf8','ignore')
            self.html = content
            ret.append(content)
            return content
        except:
            return None
    
    def getFriends(self, userid):
        friendlist = set()
        maxpage = 0
        m1 = r'<a href="http://www.renren.com/profile.do\?id=\d+">[^<>]+</a>'
        m2 = r'curpage=\d+'
        patternid = re.compile(r'\d+')
        pattern1 = re.compile(m1)
        pattern2 = re.compile(m2)
        curpage = 0
#         print 'crawling ', r'http://friend.renren.com/GetFriendList.do?id='+userid
        while curpage <= maxpage:
            url = r'http://friend.renren.com/GetFriendList.do?curpage=' +str(curpage)+'&id='+userid 
            ret = []
            content = self.TIMEOUT(self.getHtml, url, ret)[0]
#             print content
#             content = self.getHtml(url)
            if content is None:
                continue
            matches = pattern1.findall(content)
#             for m in matches:
#                 print m
            matches2 = pattern2.findall(content)
            for page in matches2:
                if int(page[page.index('=')+1:]) > maxpage:
                    maxpage = int(page[page.index('=')+1:])
            for id in matches:
                friendlist.add(str(patternid.findall(id)[0]))
            curpage = curpage + 1
        self.saveFriendList(userid, friendlist)
        return friendlist
    
    def saveFriendList(self, userid, friendlist, directory='friendlist'):
        currentdir = os.path.abspath('.')
        frienddir = os.path.join(currentdir, directory)
        if not os.path.exists(frienddir):
            os.mkdir(frienddir)
        filepath = ''
        if len(friendlist) == 0:
            filepath = os.path.join(frienddir,'getfail.txt')
            if not os.path.exists(filepath):
                fid = open(filepath,'wb')
            else:
                fid = open(filepath, 'ab')
            fid.write(userid+'\n')
            fid.close()
        else:
            filepath = os.path.join(frienddir, userid+'.txt')
            fid = open(filepath,'wb')
            for id in friendlist:
                fid.write(id+'\n')
            fid.close()
        
    def TIMEOUT(self, func, *args, **kwargs):
        second = 10
        ret = args[-1]
        th = threading.Thread(target = func, args = args, kwargs=kwargs)
        th.setDaemon(True)
        th.start()
        th.join(second)
        if th.isAlive():
            print 'ignore and time out 10'
        return ret
    
    def accessMainpage(self, userid):
        '''subthread'''
        global lock
        global semaphore
        global level_list
        print userid
        lst = []
        while True:
            if semaphore.acquire():
                lst = self.getFriends(userid)
                self.save(userid)
                semaphore.release()
                break
        while True:
            if lock.acquire():
                level_list.update(lst)
                lock.release()
                break
    def saveUrlContent(self,url,path):
        if os.path.exists(path):
            return
#         print url
        content = self.getHtml(url)
        if content is None:
            return
        if not content.find('http://icode.renren.com/getcode.do') == -1:
            print 'CODE'
            return
        fid = open(path, 'wb')
        fid.write(content)
        fid.close()
    
    def save(self, userid, directory='download'):
#         print 'save user: ',userid
        currentpath = os.path.abspath('.')
        dowloadpath = os.path.join(currentpath, directory)
        path = os.path.join(dowloadpath, str(userid))
        if not os.path.exists(path):
#             print 'making dir ', path
            os.makedirs(path)
        filepath = []
        filepath.append(os.path.join(path,str(userid)+'_mainpage.html'))
#         filepath.append(os.path.join(path,str(userid)+'_profile.html'))
#         filepath.append(os.path.join(path,str(userid)+'_album.html'))
        urls = []
#         urls.append(r'http://www.renren.com/profile.do?id=' + str(userid))
#         urls.append(r'http://www.renren.com/%s/profile?v=info_timeline'%userid)
        urls.append(r'http://photo.renren.com/photo/%s/album/relatives'%userid)
         
        for index in range(len(urls)):
            url = urls[index]
            path = filepath[index]
            self.saveUrlContent(url, path)
        
    def getFriendsByLevel(self, level=0):
        global level_list
        global levelfriendlist
        
        level_list.add(self._id)
#         self.removeDuplication()
        friendlist = level_list
        baselevel = 0
        while baselevel <= level:
            if len(level_list)==0:
                print 'stop'
                return
#             print 'level number is ', len(level_list)
            level_list = set()
            threadlist = []
            print 'level:',baselevel
            print 'fried list: ',len(friendlist)
            while len(friendlist):
                userid = friendlist.pop()
#                 print 'userid: ',userid
                th = threading.Thread(target= self.accessMainpage, args=(userid,))
                threadlist.append(th)
            counter = 0
            print 'finish creating threads'
            print 'starting threads'
            templist = []
            for th in threadlist:
                th.start()
                templist.append(th)
                while len(templist)>50:
                    counter = 0
                    for t in templist:
                        if t.isAlive():
                            counter += 1
                        else:
                            templist.remove(t)
                    if counter > 20:
                        print 'the number running threads exceeds 20'
                        time.sleep(3)
                    else:
                        break
                    
                    
#                 if counter >= 100:
#                     print 'threads number 100, waiting 10 seconds'
#                     time.sleep(10)
#                     counter = 0
#                 counter = counter + 1
            
            iswait = True
            print 'waiting for threads to finish that still alive'
            while iswait:
                iswait = False
                for th in threadlist:
                    if th.is_alive():
                        iswait = True
                        break
#                     else:
#                         threadlist.pop()
                        
            print 'all threads finish'
            print 'remove duplication'
#             self.removeDuplication()
            print 'finish remove duplication'
            print 'level finish'
            friendlist = level_list
            baselevel = baselevel + 1
            print 'number: ',len(level_list) 
                
    def removeDuplication(self):
        global levelfriendlist
        global level_list
        global lock
        total = set()
        print 'before remove:', len(level_list)
        for level in levelfriendlist:
            total.update(level)
        while True:
            if lock.acquire():
                temp = copy.deepcopy(level_list)
                for friendid in level_list:
                    if total.__contains__(friendid):
                        temp.remove(friendid)
                
                levelfriendlist.append(temp)
                level_list = copy.deepcopy(temp)
                lock.release()
                break
        print 'after remove:',len(level_list)
    

def TimeOut(func, *args, **kwargs):
    second = args[0]
    args = args[1:]
    th = threading.Thread(target = func, args=args, kwargs=kwargs)
    th.start()
    th.join(second)
#     th.kill()
    print 'thread timeout %s' % second
    if th.isAlive():
        print 'timeout and kill'
        return
    
def pp(sec):
    print 'waiting %s seconds' % sec
    time.sleep(1)

if __name__=='__main__':
#     TimeOut(pp,2,100)
    c = crawler("meditative@163.com","53894332lt")
    c.login()
    c.getFriendsByLevel(10000)