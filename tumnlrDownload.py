import urllib2
import urllib
import re, sys, os, time
from multiprocessing import Pool
#0918 by cuoge.
def writeTask(imgx,fileFullName):
    urllib.urlretrieve(imgx,fileFullName )

def delOldFile(dirName):
    i=0;
    nowTime = time.time()
    for filename in os.listdir(dirName):
        targetFile = os.path.join(dirName,  filename)
        interTime = nowTime - os.stat(targetFile).st_mtime
        if interTime > 3600*24*2:
            os.remove(targetFile)
            i=i+1
    print 'Deleted file num:%d'  %i

def downLoadFunc(blogName,srcNum,savePath,isParallel):  #savapath need a '/' as the tail.
    extractpicre = re.compile(r'(?<=<photo-url max-width="1280">).+?(?=</photo-url>)',flags=re.S)   #search for url of maxium size of a picture, which starts with '<photo-url max-width="1280">' and ends with '</photo-url>'
    outputPath = savePath+'%s.txt' %blogName.strip()
    outputfile = open(outputPath,'w') #output for writing extracted urls
    proxy= {'http':'http://172.16.0.223:9090'} #proxy setting for some reason
    showNum = 10
    baseurl = 'http://'+blogName.strip()+'.tumblr.com/api/read?type=photo&num=%d&start=' %showNum   #url to start with
    fortime = urllib.urlopen('http://'+blogName.strip()+'.tumblr.com/api/read?type=photo&num=1&start=0').read()
    temper = re.compile(r'(?<=date-gmt=").+?(?=GMT)',flags=re.S)
    freshtime = temper.findall(fortime)
    #print freshtime
    start = 0   #start from num zero
    while True: #loop for fetching pages
        url = baseurl + str(start)  #url to fetch
	#print url
        #print url   #show fetching info
        pagecontent = urllib.urlopen(url).read()   #, proxies = proxy).read()    #fetched content
        pics = extractpicre.findall(pagecontent)    #find all picture urls fit the regex
        for picurl in pics: #loop for writing urls
            outputfile.write(picurl + '\n') #write urls to text file
        if (len(pics) < showNum or start >= srcNum):    #figure our if this is the last page. if less than 50 result were found 
            break   #end the loop of fetching pages
        else:   #find 50 result
            start += showNum #heading to next page
    outputfile.close()  #close the output file
    allNum = len(open(savePath+'%s.txt' %blogName.strip(),'rU').readlines())
    outputfile = open(outputPath,'r') #output for writing extracted urls
    x=0;
    print('Begin to download...')
    tempPath = savePath+blogName.strip() 
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)
    if isParallel==1:
        p = Pool(16)  # multi processes.
        for imgx in outputfile:
            fileName = imgx[str(imgx).rfind('/')+1:].strip()
            fileFullName = savePath+blogName.strip()+'/'+fileName
            if not os.path.isfile(fileFullName):
                p.apply_async(writeTask,args=(imgx,fileFullName))

            else:
                os.system(r'touch %s' % fileFullName)
        p.close()
        p.join()
    else:
        for imgx in outputfile:
            #x += 1
            fileName = imgx[str(imgx).rfind('/')+1:].strip()
            fileFullName = savePath+blogName.strip()+'/'+fileName
            if not os.path.isfile(fileFullName):
                urllib.urlretrieve(imgx,fileFullName )
            #if x%stepNum == 1:
                #sys.stdout.write("%d%%\r" %(100*x/allNum) )
                #sys.stdout.flush()
            #sys.stdout.write("%d%%" %(100*x/allNum) )
            #sys.stdout.flush()
            #sys.stdout.write("\n")
    print'There are %d files should have been finished from http://' %allNum + blogName.strip() 
    outputfile.close()
    os.remove(outputPath)
    return freshtime[0].strip()

start = time.time()
srcNum = 30
totalPath = '/usr/share/nginx1/html/tumblrDir/'
inputfile = open(totalPath+'blogname.txt','r')    #input file for reading blog names (subdomains). one per line
tempblog = open(totalPath+'blogname2.txt','w') 
isParallel = 1
for blogper in inputfile:
    blogEach = blogper.strip().split('.')[0]
    freshtime = downLoadFunc(blogEach,srcNum,totalPath,isParallel)
    dirName = totalPath + blogEach.strip()
    delOldFile(dirName)
    tempblog.write( blogEach+'.'+freshtime+'\n' )
    #break
inputfile.close()
tempblog.close()
os.remove(totalPath+'blogname.txt')
os.rename(totalPath+'blogname2.txt',totalPath+'blogname.txt')
print'Congratulations! All have been finished!'
end = time.time()
print 'Tasks run %0.2f seconds.' % (end - start)

