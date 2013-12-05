
'''
Created on 2013-11-24

@author: Tony
'''

import urllib2
import os
import re
import time

def saveUrl(url, filename, directory):
    req = urllib2.Request(url)
    content = urllib2.urlopen(req).read()
    current = os.path.abspath('.')
    dir = os.path.join(current, directory)
    if not os.path.exists(dir):
        os.makedirs(dir)
    filename = os.path.join(dir, filename)
    fid = open(filename, 'wb')
    fid.write(content)
    fid.close()
    return content
    
def accessByYear(year):
    url = r'http://www.soopat.com/Home/Result?SearchWord=SQRQ%3A('+str(year)+')%20SQR%3A(%20%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6)%20'
    req = urllib2.Request(url)
    content = urllib2.urlopen(req).read().decode('utf8','ignore').encode('gbk','ignore')
    time.sleep(3)
##    current = os.path.abspath('.')
##    file_path = os.path.join(current, 'zl' ,'2010.html')
##    print file_path
##    fid = open(file_path, 'rb')
##    content = fid.read()
##    fid.close()
##    content = content.decode('utf8','ignore').encode('gbk','ignore')
    
    p = r'\d+</b>Ïî·ûºÏ'
    patt = re.compile(p)
    matches = patt.findall(content)
    print matches
    counter = matches[0][0:matches[0].index('<')]
    total_page = int(counter)/10
    print 'total pages = ',total_page
    for index in range(0,total_page+1):
        accessYearBypage(year, index)
        time.sleep(3)
        
    
    
def accessYearBypage(year, page_index):
    print 'year = ',year,', page_index = ',page_index
    url = r'http://www.soopat.com/Home/Result?SearchWord=SQRQ%3A('+str(year)+')%20SQR%3A(%20%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6)%20'+'&PatentIndex='+str(page_index*10)
    print url
    saveUrl(url, str(year)+'_'+str(page_index)+'.html', 'pages' )


def parserSQHByYear(year):
    current = os.path.abspath('.')
    file_list = os.listdir(os.path.join(current, 'pages'))
#    print file_list
    p = r'SQH=\'\d+\''
    pattern = re.compile(p)
    SQH_path = os.path.join(os.path.join(current, 'SQH', str(year) + '.txt'))
    fidw = open(SQH_path, 'wb')
    for fn in file_list:
        if not fn.startswith(str(year)):
        #    print 'start with'
            continue
        file_path = os.path.join(os.path.join(current, 'pages', fn))
        if not os.path.isfile(file_path):
       #     print 'file'
            continue
        fid = open(file_path, 'rb')
        content = fid.read()
        fid.close()
        print file_path
        matches = pattern.findall(content)
        
        for item in matches:
            print item
            print item[4:-1]
            fidw.writelines(item[5:-1]+'\n')
    fidw.close()

def getPatentByYear(year):
    current = os.path.abspath('.')
    SQH_path = os.path.join(os.path.join(current, 'SQH', str(year) + '.txt'))
    if not os.path.exists(SQH_path):
        print 'file error'
        return False
    fidr = open(SQH_path, 'rb')
    line = fidr.readline()
    
    base_url = r'http://www.soopat.com/Patent/'
    print '---------',year,'-----------'
    while line:
        SQH_id = line.strip()
        url = base_url + SQH_id
        print 'accessing ',url
        save_path = os.path.join(current, 'Patent', str(year))
        saveUrl(url, str(SQH_id)+'.html', save_path)
        time.sleep(3)
        line = fidr.readline()
    fidr.close()

def getPatent():
    ran = range(2003,2014)
    for year in ran:
        getPatentByYear(year)
    

def parserSQH():
    ran = range(1985,2014)
    for year in ran:
        parserSQHByYear(year)
    
def search():
    ran = range(2011,2014)
    for year in ran:
        print '----------------',year,'-----------------------'
        accessByYear(year)
    

    
if __name__=='__main__':
    getPatent()
