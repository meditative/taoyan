'''
Created on Jul 11, 2013

@author: tonyliu
'''
import os, time
import threading
import urllib2

backupfolder = "/sandbox/Backups"

def rmDirOrFile(src):
    '''delete file or folder'''
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            print "remove file", src , " fail"
            return 0
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            rmDirOrFile(itemsrc)
        try:
            print "removing ",src
            os.rmdir(src)
            return 1
        except:
            print "remove dir ", src , "fail"
            return 0

def rmFileByName(SrcDir, rmItem):
    '''remove all files and folders named rmItem in SrcDir'''
    if os.path.isfile(SrcDir):
        print SrcDir , " is a file, not a folder"
        return 0
    else:
        for item in os.listdir(SrcDir):
            itempath = os.path.join(SrcDir,item)
            try:
                if rmItem == item :
                    print itempath ," is removing..."
                    rmDirOrFile(itempath)
                else:
                    rmFileByName(itempath, rmItem)
            except:
                print "remove ",itempath," fail"
        return 1
    
    
def copy(Src, Des):
    '''file copy, Copy Src to Des'''
    if not os.path.exists(Des) :
        print "The Destination is not exit"
        return 0
    if not os.path.exists(Src):
        print "The source is not exit"
        return 0
    else:
        [dir,filename] = os.path.split(Src)
        path = os.path.join(Des,filename)
        if os.path.exists(path):
            rmDirOrFile(path)
        if os.path.isfile(Src):
            print "copying ",Src ,"--to-->",path
            open(path, "wb").write(open(Src, "rb").read())
        else:
            if os.path.isdir(Src):
                os.mkdir(path)
            for file in os.listdir(Src):
                filepath = os.path.join(Src,file)
                if os.path.isfile(filepath):
                    print "copying ",filepath ," to ",os.path.join(path,file)
                    open(os.path.join(path,file), "wb").write(open(filepath, "rb").read())
                elif os.path.isdir(Src):
                    print "copying folder ",filepath ," to ",path
                    copy(filepath,path)
        return 1    
    
def copyByType(Src, Des,type):
    '''only copy all the "type" files in folder "Src" to folder "Des". the relative path of "type" files are same.
    Src --> source
    Des --> destination
    type --> file type
    '''
    if not os.path.exists(Src):
        print "The source is not exit"
        return 0
    else:
        [dir,filename] = os.path.split(Src)
        path = os.path.join(Des,filename)
        if os.path.isfile(Src):
            if Src.split(r".")[-1] == type:
                if not os.path.exists(Des):
                    os.makedirs(Des)
                print "copying ",Src ,"--to-->",path
                open(path, "wb").write(open(Src, "rb").read())
        else:
            for file in os.listdir(Src):
                filepath = os.path.join(Src,file)
                if os.path.isfile(filepath):
                    if file.split(r".")[-1] == type:
                        print Src
                        print path
                        print Des
                        if not os.path.exists(path):
                            print "making dirs   ",path
                            os.makedirs(path)
                        print "copying ",filepath ," to ",os.path.join(path,file)
                        open(os.path.join(path,file), "wb").write(open(filepath, "rb").read())
                elif os.path.isdir(Src):
                    print "copying folder ",filepath ," to ",path
                    copyByType(filepath,path,type)
        return 1
    
    
    
def replaceFileInDir( replacefile,SrcDir):
    '''replace all files named replacefile in SrcDir'''
    if not os.path.isfile(replacefile):
        print replacefile ," is not exist"
        return 0
    if not os.path.isdir(SrcDir):
        print SrcDir , " is not a folder"
        return 0
    [dir,filename] = os.path.split(replacefile)
    
    for file in os.listdir(SrcDir):
        filepath = os.path.join(SrcDir,file)
        if os.path.isfile(filepath) and file == filename:
            replaceFile(replacefile,filepath)
        if os.path.isdir(filepath):
            replaceFileInDir(replacefile,filepath)
    return 1
    
    
def replaceFile(srcfile,desfile):
    '''use srcfile to replace srcfile'''
    if not os.path.isfile(srcfile):
        print srcfile , " is not a file"
        return 0
    if not os.path.exists(desfile):
        print desfile , " is not exist"
        return 0
    try:
        print "delete ", desfile
        os.remove(desfile);
    except:
        print "delete ", desfile, " fail"
        return 0
    print "copy (replace)"
    open(desfile, "wb").write(open(srcfile, "rb").read())
    return 1
    
def backup(files, backup = backupfolder):
    '''backup files to folder backup, the backupfolder is default'''
    if not os.path.isdir(backup):
        try:
            print "making dir..."
            os.mkdir(backup)
        except:
            print "making dir fail"
            return 0
    print "The backup folder is ", backupfolder
    if not os.path.exists(files):
        print "The backup file ",files , "is not exist. Please check the path"
        return 0
    [dir, filename ] = os.path.split(files)
    backuptime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    backuppath = os.path.join(backup, filename + "_" + backuptime)
    try:
        os.mkdir(backuppath)
    except:
        pass
    copy(files, backuppath)
    return 1
    
def replaceStringInFile(file, str, replace ):
    '''replace "str" with "replace" in file "file"'''
    if not os.path.isfile(file):
        print "File ",file , " is not a file."
        return 0
    try:
        [dir , filename] = os.path.split(file)
        tmpfile = os.path.join(dir,"tmp")
        
        open(tmpfile, "wb").write(open(file, "rb").read())

        fidr = open(tmpfile,'rb')
        fidw = open(file,'wb')
        lines = fidr.readlines()
        for s in lines:
            fidw.write(s.replace(str,replace))
        fidr.close()
        fidw.close()
        os.remove(tmpfile)
        print "success"
        return 1
    except:
        return 0
    
def replaceStringInFolder(folder, str, replace,filetype = "" ):
    '''replace string "str" with "replace" in files with a type of "filetype" in folder "folder"'''
    if not os.path.isdir(folder):
        print folder , " is not a folder"
        return 0
    for file in os.listdir(folder):
        filepath = os.path.join(folder,file)
        if os.path.isfile(filepath):
            if filetype == file.split(r".")[-1]:
                replaceStringInFile(os.path.join(folder,file), str, replace )
        if os.path.isdir(filepath):
            replaceStringInFolder(filepath,str, replace,filetype)
    return 1
    
def filterFileByType(src, des, type):
    '''choose files in src with type of "type" and copy them to des folder'''
    if not os.path.exists(src):
        print "the source ", src , "is not exist"
        return 0
    if not os.path.isdir(des):
        print "the destination ", des, "is not a folder, please choose a folder"
        try:
            print "making folder ", des
            os.makedirs(des)
        except:
            print "making folder ", des, " fail"
            return 0
#        return 0
    if type == "":
        print "please set the file type that is used to filter files"
        return 0
    for file in os.listdir(src):
        filepath = os.path.join(src, file)
        if os.path.isdir(filepath):
            filterFileByType(filepath,des,type)
        if os.path.isfile(filepath) and type == file.split(".")[-1]:
            copy(filepath, des)
    
def fileExistListener(filename):
    '''a listener that is used to listening filename'''
    while True:
        if os.path.exists(filename):
#            thread.start_new_thread(copy, [filename,filename])
            time.sleep(10)
            copy(filename,filename)
        else:
            time.sleep(10)
            
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
    
def TimeOut(func, *args, **kwargs):
    second = args[0]
    args = args[1:]
    th = threading.Thread(target = func, args=args, kwargs=kwargs)
    th.start()
    th.join(second)
    th.kill()
    print 'thread timeout %s' % second
    if th.isAlive():
        print 'timeout and kill'
        return
    
if __name__=="__main__":
    import time
#     url = r'http://www.soopat.com/Home/Result?SearchWord=SQRQ%3A(1988)%20SQR%3A(%20%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6)%20'
    ran = range(1987,2014)
    for year in ran:
        url = r'http://www.soopat.com/Home/Result?SearchWord=SQRQ%3A('+str(year)+')%20SQR%3A(%20%E5%8D%97%E4%BA%AC%E5%A4%A7%E5%AD%A6)%20'
        print url
        saveUrl(url, str(year)+'.html', 'zl')
        time.sleep(3)
    
    