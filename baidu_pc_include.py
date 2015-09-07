#coding:utf-8
'''
百度收录查询，多线程代理随机代理版本
'''
import StringIO,pycurl,time,random,re,os,csv,urllib,urllib2
from threading import Thread,Lock
from Queue import Queue
from bs4 import BeautifulSoup as bs

bdjd_dict = {}
daili_list = [] #存储代理ip
def ip():
    for x in open('hege_daili.txt'):
        x = x.strip()
        daili_list.append(x)
    newip = random.choice(daili_list)
    return newip

#如果代理不可用，则从代理文件中删除，此函数在baidu_cout中应用
def daili_delete(ip):
    dailifile = open('daili_beifen.txt','w')
    for line in open('hege_daili.txt'):
        line = line.strip()
        if ip not in line:
            dailifile.write(line+"\n")
    os.system("mv daili_beifen.txt hege_daili.txt")

resultname = time.strftime('%Y%m%d',time.localtime(time.time()))    #获取当前日期
resultfile = open('include_result','w')   #以当前日期为文件名，将收录结果保存于此文件中
start_time = time.time()

#bdjd_list = ["www.baidu.com","180.97.33.107","115.239.210.27","180.97.33.108","180.97.33.107","180.97.33.107","180.97.33.108","220.181.111.188","220.181.111.188","180.97.33.107","180.97.33.107","115.239.211.112","180.97.33.108","180.97.33.108","180.97.33.108","180.97.33.108","180.97.33.108","115.239.211.112","180.97.33.108","115.239.211.112","115.239.210.27","180.97.33.108","115.239.211.112","115.239.210.27","180.97.33.108","115.239.210.27","61.135.169.125","115.239.211.112","115.239.210.27","180.97.33.107","180.97.33.107","180.97.33.108","115.239.210.27","180.97.33.107","61.135.169.121","115.239.210.27","61.135.169.121","61.135.169.125","115.239.211.112","115.239.210.27","61.135.169.125","112.80.248.73","61.135.169.121","112.80.248.74","112.80.248.73","61.135.169.125","180.97.33.108","115.239.210.27","61.135.169.125","61.135.169.125","112.80.248.74","112.80.248.74","61.135.169.121","115.239.210.27","61.135.169.125","111.13.100.92","111.13.100.92","111.13.100.91","111.13.100.91","115.239.211.112","111.13.100.92","111.13.100.91","111.13.100.92","115.239.211.112","115.239.210.27","115.239.211.112","115.239.210.27","115.239.210.27","115.239.210.27","115.239.210.27"]

bdjd_list = ["www.baidu.com"]

#定义UA
def getUA():
    uaList = ['Mozilla/4.0+(compatible;+MSIE+6.0;+Windows+NT+5.1;+SV1;+.NET+CLR+1.1.4322;+TencentTraveler)',
    'Mozilla/4.0+(compatible;+MSIE+6.0;+Windows+NT+5.1;+SV1;+.NET+CLR+2.0.50727;+.NET+CLR+3.0.4506.2152;+.NET+CLR+3.5.30729)',
    'Mozilla/5.0+(Windows+NT+5.1)+AppleWebKit/537.1+(KHTML,+like+Gecko)+Chrome/21.0.1180.89+Safari/537.1',
    'Mozilla/4.0+(compatible;+MSIE+6.0;+Windows+NT+5.1;+SV1)',
    'Mozilla/5.0+(Windows+NT+6.1;+rv:11.0)+Gecko/20100101+Firefox/11.0',
    'Mozilla/4.0+(compatible;+MSIE+8.0;+Windows+NT+5.1;+Trident/4.0;+SV1)',
    'Mozilla/4.0+(compatible;+MSIE+8.0;+Windows+NT+5.1;+Trident/4.0;+GTB7.1;+.NET+CLR+2.0.50727)',
    'Mozilla/4.0+(compatible;+MSIE+8.0;+Windows+NT+5.1;+Trident/4.0;+KB974489)',
    'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'
    ]
    headers = random.choice(uaList)
    return headers


#提取百度地域节点
def getBDJD(bdjd_str):
    bdjd_list = bdjd_str.split(',')
    bdjd = random.choice(bdjd_list)
    return bdjd

#获取源码
def is_index(line,headers):
    while 1:
        try:
            url = 'http://www.baidu.com/s?wd=%s' % urllib.quote_plus(line.strip())
            c = pycurl.Curl()
            c.setopt(pycurl.MAXREDIRS,5)
            c.setopt(pycurl.REFERER, url)
            c.setopt(pycurl.FOLLOWLOCATION, True)
            c.setopt(pycurl.CONNECTTIMEOUT, 120)
            c.setopt(pycurl.TIMEOUT,120)
            c.setopt(pycurl.ENCODING,'gzip,deflate')
            #c.setopt(c.PROXY,ip)
            c.fp = StringIO.StringIO()
            c.setopt(pycurl.URL, url)
            c.setopt(pycurl.HTTPHEADER,headers)
            c.setopt(c.WRITEFUNCTION, c.fp.write)
            c.perform()
            #code = c.getinfo(c.HTTP_CODE) 返回状态码
            html = c.fp.getvalue()
            if '="http://verify.baidu.com' in html:
                print "出验证码"
                time.sleep(10)
                continue
            else:
                return html
        except Exception, what:
            information = '错误信息：%s' % what
            return str(information)
            continue
            

#正则提取模块
def search(req,line):
    text = re.search(req,line)
    if text:
        data = text.group(1)
    else:
        data = 'no'
    return data

url_list = []
for line in open('url_str'):
    url = line.strip()
    url_list.append(url)


class Fetcher:
    def __init__(self,threads):
        self.lock = Lock() #线程锁
        self.q_req = Queue() #任务队列
        self.q_ans = Queue() #完成队列
        self.threads = threads
        for i in range(threads):
            t = Thread(target=self.threadget) #括号中的是每次线程要执行的任务
            t.setDaemon(True) #设置子线程是否随主线程一起结束，必须在start()
                              #之前调用。默认为False
            t.start() #启动线程
        self.running = 0 #设置运行中的线程个数
 
    def __del__(self): #解构时需等待两个队列完成
        time.sleep(0.5)
        self.q_req.join() #Queue等待队列为空后再执行其他操作
        self.q_ans.join()
 
    #返回还在运行线程的个数，为0时表示全部运行完毕
    def taskleft(self):
        return self.q_req.qsize()+self.q_ans.qsize()+self.running 

    def push(self,req):
        self.q_req.put(req)
 
    def pop(self):
        return self.q_ans.get()
 
	#线程执行的任务，根据req来区分 
    def threadget(self):
        while True:
            line = self.q_req.get()
            line = line.strip()

            '''
            Lock.lock()操作，使用with可以不用显示调用acquire和release，
            这里锁住线程，使得self.running加1表示运行中的线程加1，
            如此做防止其他线程修改该值，造成混乱。
            with下的语句结束后自动解锁。
            '''

            with self.lock: 
                self.running += 1

            headers = [
                "Accept:text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Encoding:gzip, deflate, sdch",
                "Accept-Language:zh-CN,zh;q=0.8,en;q=0.6",
                "Cache-Control:max-age=0",
                "Connection:keep-alive",
                #"Cookie:BAIDUID=18BFE1C8A802F8458F26D043CD7CD624:FG=1; BDUSS=lpaNUg2NkloQTBKVVh4aVBsczJNLUc2QjEzN05wMXUzeE50WXZSQVNaRmU3WlZWQVFBQUFBJCQAAAAAAAAAAAEAAAAJkstJv7TXvMTj1NnM-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAF5gblVeYG5Vb; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a01833473155; BDSFRCVID=Vy8sJeCCxG3TKh3lHco6WY5CFWPhzzDzLlKH3J; H_BDCLCKID_SF=JbAjoKK5tKvbfP0kh-QJhnQH-UnLq5JIH67Z0lOnMp05ShvdDPv12bTL-q5mhU70LIbEXqbLBnRvOKO_e6t5D5J0jN-s-bbfHDJK0b7aHJOoDDvK2j75y4LdLp7xJh3i2n7QanOOJf3ZMqOD3p3s2RIv24vQBMkeWJQ2QJ8BJD_2hI3P; BIDUPSID=18BFE1C8A802F8458F26D043CD7CD624; PSTM=1433406316; BDRCVFR[ltbVPlNi2ac]=mk3SLVN4HKm; BD_UPN=123253; sug=3; sugstore=1; ORIGIN=0; bdime=0; H_PS_645EC=2002DrwijyvB4e2cepMJ9FuSgzu6vKJjbMOeRrfZjipiNRVem6mc9uqx%2FBzqlM7Z; BD_CK_SAM=1; BDSVRTM=14; H_PS_PSSID=13372_1428_14602_12772_14509_14444_10812_14600_12868_14622_10562_14501_12723_14626_14485_14244_11460_13936_8498
                "Host:www.baidu.com",
                "RA-Sid:7739A016-20140918-030243-3adabf-48f828",
                "RA-Ver:2.10.4",
                "User-Agent:%s" % getUA()
            ]    



            bdjd_str = ','.join(bdjd_list)

            newip = ip()
            bdjd = getBDJD(bdjd_str)
            html = is_index(line,headers)

            # if '错误信息' in html:
            #     print html
            #     if 'Connection refused' in html:
            #         #判断访问超时的节点存入字典，若该节点已超过10次链接超时，则从节点列表中删除
            #         if bdjd_dict.has_key(bdjd):
            #             bdjd_dict[bdjd] += 1
            #             print '节点：%s，已%s次超时' % (bdjd,bdjd_dict[bdjd])
            #             if int(bdjd_dict[bdjd]) >= 10:
            #                 bdjd_list.remove(bdjd)
            #                 print "节点：%s 已删除" % bdjd
            #         else:
            
            if '抱歉，没有找到与' in html or '没有找到该URL' in html:
                print "url：%s，未收" % line
                resultfile.write("%s,未收\n" % line)
            else:
                print "url：%s，已收" % line
                resultfile.write("%s,已收\n" % line)

            #self.q_ans.put((req,ans)) # 将完成的任务压入完成队列，在主程序中返回
            self.q_ans.put(line)
            with self.lock:
                self.running -= 1
            self.q_req.task_done() # 在完成一项工作之后，Queue.task_done()
                                   # 函数向任务已经完成的队列发送一个信号
            time.sleep(0.1) # don't spam
 
if __name__ == "__main__":
    f = Fetcher(threads=10) #设置线程数为10
    for url in url_list:
        f.push(url)         #所有url推入下载队列
    while f.taskleft():     #若还有未完成的的线程
        f.pop()   #从下载完成的队列中取出结果
          




