# -*- coding: utf-8 -*-
import re
from RobotBase import RobotParseBase
import httplib2
import sqlite3

class RobotList(RobotParseBase):
    def __init__(self, db_type=0):
        RobotParseBase.__init__(self, db_type)
        self.__html=str()
        #self.set_tag('1989')
        self.result=[]

    def set_tag(self, tag):
        #/x3d转换为%3d
        self.tag=self.url_encode(tag)
        self.untag=tag

    def get_tag(self):
        return self.tag

    def get_ids(self, movie_count):
        '''
        对每个标签，获得（指定数目的）页面id，返回列表，没有为[]
        '''
        tag=self.get_tag()
        movie_url=self.get_domain()+'tag/%(tag)s'%{'tag':self.tag}
        headers=self.get_headers()
        url=movie_url+'?start=%d'%(movie_count)
        h=httplib2.Http()
        try:
            resp, movie_html=h.request(url, "GET", headers=headers)
        except (httplib2.ServerNotFoundError), e:
            print e
            return False
        self.set_html(movie_html)
        return True

    def parse_ids(self):
        '''
        获得页面中所有id，返回id列表，没有返回[]
        '''
        ids_re=r'nbg" href="http://(book|music|movie)\.douban\.com/subject/(\d+)/.*?title="(.*?)"'
        ids_pattern=re.compile(ids_re, re.S)
        ids_res=ids_pattern.findall(self.get_html())
        ids_list=list()
        for i in range(len(ids_res)):
            ids_list.append((int(ids_res[i][1]), ids_res[i][2]))
            #TYPE(num, 'title')
        return ids_list

    def save_ids(self):
        '''
        save the lists in database
        '''
        tag=self.untag.decode('utf-8')
        if not self.init_db():
            return False
        cur=self.conn.cursor()
        op="""SELECT tid 
            From tags 
            WHERE content=='%s' AND type==%d"""%(tag, self.dbt)
        cur.execute(op)
        ret=cur.fetchone()
        if not ret:
            return False
        tid=ret[0]
        op="""SELECT sid
            FROM lists
            WHERE tid=%d
        """%tid
        cur.execute(op)
        rets=[ret[0] for ret in cur]
        for sid, tittle in self.result:
            if sid in rets:
                continue
            op="""INSERT INTO lists (sid, tid, done, tittle)
                VALUES (?, ?, ?, ?)
            """
            vals=(sid, tid, 0, self.utf82uni(tittle))
            cur.execute(op, vals)
        if not self.finish_db():
            return False
        return True

    def read_ids(self):
        '''
        load the lists in database
        '''
        tag=self.untag.decode('utf-8')
        if not self.init_db():
            return False
        cur=self.conn.cursor()
        op="""SELECT tid
            FROM tags
            WHERE content=='%s' AND type==%d
        """%(tag, self.dbt)
        cur.execute(op)
        ret=cur.fetchone()
        if not ret:
            return False
        tid=ret[0]
        op="""SELECT sid, tittle
            FROM lists
            WHERE tid=%d
        """%tid
        cur.execute(op)
        rets=[(ret[0], self.uni2utf8(ret[1])) for ret in cur]
        if not rets:
            return False
        self.result=rets
        return True

    def netstart(self, tag):
        '''
        对每个标签，获得（指定数目的）页面id，返回列表，没有为[]
        '''
        movie_pid=0
        self.set_tag(tag)
        movie_urls=list()
        while True:
            if not self.get_ids(movie_pid):
                return False
            res_urls=self.parse_ids()
            if not res_urls:
                break
            movie_urls.extend(res_urls)
            movie_pid+=20
        self.result=movie_urls
        self.count=len(self.result)
        return self.save_ids()

    def localstart(self, tag):
        '''
        本机读取id
        '''
        self.set_tag(tag)
        if not self.read_ids():
            return self.netstart(tag)
        self.count=len(self.result)
        return True
    
if __name__=='__main__':
    r=RobotList()
    r.netstart("1989")
