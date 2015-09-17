import urllib2
import urllib
import re, sys, os, time
from multiprocessing import Pool
from bs4 import BeautifulSoup
import HTMLParser

def writeTask(imgx,fileFullName):
    urllib.urlretrieve(imgx,fileFullName )

def delOldFile(dirName):
    i=0;
    nowTime = time.time()
    for filename in os.listdir(dirName):
        targetFile = os.path.join(dirName,  filename)
        interTime = nowTime - os.stat(targetFile).st_mtime
        if interTime > 7200:
            os.remove(targetFile)
            i=i+1
    print 'Deleted file num:%d'  %i

def downLoadFunc(blogName,srcNum,savePath,isParallel):  #savapath need a '/' as the tail.
    outputPath = savePath+'%s.txt' %blogName.strip()
    outputfile = open(outputPath,'w') #output for writing extracted urls
    proxy= {'http':'http://172.16.0.223:9090'} #proxy setting for some reason
    showNum = 10
    baseurl = 'http://'+blogName.strip()+'.tumblr.com/api/read?type=video&num=%d&start=' %showNum   #url to start with
    start = 0   #start from num zero
    html_parser = HTMLParser.HTMLParser()
    while True: #loop for fetching pages
        url = baseurl + str(start)  #url to fetch
        #print url   #show fetching info
        pagecontent = urllib.urlopen(url).read()#, proxies = proxy).read()    #fetched content
        soup = BeautifulSoup(pagecontent, "lxml")
        #print soup.text
        videoSet=soup.find_all('video-player',{'max-width':"500"})
        videoSet.reverse()
        for videoEach in videoSet:
        	tempsrc =  BeautifulSoup(html_parser.unescape(str(videoEach)),"lxml").find('source')
        	if (tempsrc):
        		vidurl = str(tempsrc['src']).strip()
        		if(len(vidurl) - vidurl.rfind('/') < 5):
        			vidurl = vidurl[ : vidurl.rfind('/')]
        		outputfile.write(vidurl + '\n') #write urls to text file
        		print vidurl
        if (len(videoSet) < showNum or start >= srcNum):    #figure our if this is the last page. if less than 50 result were found 
            break   #end the loop of fetching pages
        else:   #find 50 result
            start += showNum #heading to next page
    outputfile.close()  #close the output file
    return;
    allNum = len(open(savePath+'%s.txt' %blogName.strip(),'rU').readlines())
    outputfile = open(outputPath,'r') #output for writing extracted urls
    x=0;
    print('Begin to download...')
    tempPath = savePath+blogName.strip() 
    if not os.path.exists(tempPath):
        os.makedirs(tempPath)
    if isParallel==1:
        p = Pool(8)  # multi processes.
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
                print 'finish one!'
            else:
            	os.system(r'touch %s' % fileFullName)
            #if x%stepNum == 1:
                #sys.stdout.write("%d%%\r" %(100*x/allNum) )
                #sys.stdout.flush()
    print'There are %d files should have been finished from http://' %allNum + blogName.strip() 
    outputfile.close()
    os.remove(outputPath)

def createThumbnail(videoPath,imgPath):
    for filename in os.listdir(videoPath):
        targetFile = os.path.join(videoPath.strip(),  filename.strip() )
        fileFullName = os.path.join(imgPath.strip(), filename.strip() ) + '.jpg'
        if not os.path.isfile(fileFullName):
        	os.system('sudo ffmpeg -ss 2 -i '+ targetFile +' -y -f mjpeg -t 0.001 -s 240x240 '+ fileFullName)
        else:
        	os.system(r'touch %s' % fileFullName)

start = time.time()
srcNum = 10
totalPath = '/home/cuoge/python/tumblr/'
#inputfile = open(totalPath+'blogname.txt','r')    #input file for reading blog names (subdomains). one per line
isParallel = 0
#for blogEach in inputfile:
#    downLoadFunc(blogEach,srcNum,totalPath,isParallel)
#    dirName = totalPath + blogEach.strip()
#    delOldFile(dirName)
#downLoadFunc( 'mystic-revelations' ,srcNum,totalPath,isParallel)
print'Congratulations! All have been finished!'
createThumbnail('/home/cuoge/python/tumblr/mystic-revelations/', '/home/cuoge/python/tumblr/imgpath/')
end = time.time()
print 'Tasks run %0.2f seconds.' % (end - start)

#os.system('sudo ffmpeg -ss 1 -i ./tumblr_nsb542mG381r3uvu0 -y -f mjpeg -t 0.001 -s 320x240 ./test.jpg')