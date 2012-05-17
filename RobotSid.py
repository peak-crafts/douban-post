# -*- coding: utf-8 -*-
import re
from RobotBase import RobotParseBase
import httplib2
import random
import sqlite3

#对每个Subject进行信息提取的机器人
class RobotSid(RobotParseBase):
    def __init__(self, db_type=0, cookie_path=r"cookie.txt"):
        RobotParseBase.__init__(self, db_type)
        self.__html=str()
        self.__sid=0
        #self.result=list()
        self.count=0
        self.cookie_path=cookie_path
    
    def set_sid(self, sid):
        self.__sid=sid

    def get_sid(self):
        return self.__sid

    def get_cpath(self):
        return self.cookie_path

    def get_iwanna(self):
        return self.iwanna

    def set_interest(self, i=0):
        inter=['collect', 'wish', 'do']
        iwanna=[('看过', '想看', '正在看'),
                ('听过', '想听', '正在听'),
                ('读过', '想读', '正在读'),]
        if i not in [0, 1, 2]:
            i=random.randint(0, 2)
        self.iwanna=iwanna[self.dbt][i]
        self.interest=inter[i]
        
    def get_cookie(self):
        try:
            cookie_f=open(self.get_cpath(), 'r')
        except IOError,e:
            print 'Failed in reading cookie.'
            return None
        cookie=cookie_f.readline()
        ck_re=r'ck="([0-9a-zA-Z]{4})'
        ck_pattern=re.compile(ck_re)
        ck_match=ck_pattern.search(cookie)
        if ck_match==None :
            ck=raw_input("Cannot find ck, please input:")
        else:
            ck=ck_match.group(1)
        bid='bid="d%dn%2dFuFa%dg";'%(random.randint(0, 9),
                                     random.randint(0, 99),
                                     random.randint(0, 9))
        return (cookie+bid, ck)


    def get_info(self):
        '''
        获得一页的info，返回Boolean
        '''
        comment_url=self.get_domain()+'subject/%d/'%self.get_sid()
        h=httplib2.Http()
        headers=self.get_headers()
        try:
            resp, comment_html=h.request(comment_url, "GET", headers=headers)
        except (httplib2.ServerNotFoundError), e:
            print e
            return False
        self.set_html(comment_html)
        return True
        
    def is_mark(self):
        '''
        确定是否已经阅读过，True or False
        '''
        mark_re=r'class=\\"collect_btn\\"'
        mark_pattern=re.compile(mark_re, re.S)
        mark_match=mark_pattern.search(self.get_html())
        if mark_match:
            return True
        else :
            return False

    def parse_info(self):
        '''
        获得页面中的(rate, tags, comment)，空为(0, [], '')
        '''
        rate_re=r'property="v:average">(.+?)</strong>'
        rate_pattern=re.compile(rate_re, re.S)
        rate_match=rate_pattern.search(self.get_html())
        if rate_match:
            rate_float=float(rate_match.group(1))//2+1
            rate=int(rate_float)
        else:
            rate=0
        tags_re=r'douban\.com/tag/.+?">(.+?)<'
        tags_pattern=re.compile(tags_re, re.S)
        tags=tags_pattern.findall(self.get_html())
        comment_re=r'<p class="w550">(.+?)\n'
        comment_pattern=re.compile(comment_re, re.S)
        comment_match=comment_pattern.search(self.get_html())
        if comment_match:
            comment=comment_match.group(1)
        else:
            comment=''
        self.result=(rate, tags, comment)


    def post(self):
        info=self.result
        post_url=self.get_domain()+'j/subject/%d/interest'%self.get_sid()
        post_body='ck=%(ck)s&interest=%(interest)s&rating=%(rate)d\
&foldcollect=F&tags=%(tag)s&comment=%(comment)s'
        ret=self.get_cookie()
        if ret:
            post_cookie, ck=ret
        else:
            return False
        try:
            tag='+'.join(info[1])
            tag=self.url_encode(tag)
            comment=self.url_encode(info[2])
            post_body=post_body%{'ck':ck,
                                    'interest':self.interest,
                                    'rate':info[0],
                                    'tag':tag,
                                    'comment':comment}
        except (TypeError, IndexError):
            post_body=post_body%{'ck':ck,
                                    'interest':self.interest,
                                    'rate':0,
                                    'tag':'',
                                    'comment':''}
        
        post_headers={'Cookie':post_cookie,
                      'Content-Type': 'application/x-www-form-urlencoded',
                      'User-Agent': 'Mozilla/10.0'}
        try:
            http=httplib2.Http()
            resp, content=http.request(post_url, 'POST',
                                       headers=post_headers,
                                       body=post_body)
        except httplib2.ServerNotFoundError, e:
            print e
            return False
        return True

    def start(self, sid, interest=4):
        '''
        参数是sid,执行机器人
        '''
        self.set_interest(interest)
        self.count+=1
        self.set_sid(sid)
        if not self.get_info():
            return False
        self.parse_info()
        if not self.post():
            return False
        return True

if __name__=='__main__':
    r=RobotSid()
    print r.start(4166819)
