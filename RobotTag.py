# !/usr/bin/python
# -*- coding: utf-8 -*-
import re
from RobotBase import RobotParseBase
import httplib2
import sqlite3

class RobotTag(RobotParseBase):
    def __init__(self, db_type=0):
        RobotParseBase.__init__(self, db_type)
        self.result=[]

    def save_tag(self):
        '''
        update the tag in database
        '''        
        if not self.init_db():
            return False
        cur=self.conn.cursor()
        op="SELECT content FROM tags WHERE type==%d"%self.dbt
        cur.execute(op)
        rets=[ret[0] for ret in cur]
        for tag in self.result:
            tag=self.utf82uni(tag)
            if tag in rets:
                continue
            op='''INSERT INTO tags (content, type)
                VALUES (?, ?)
            '''
            vals=(tag, self.dbt)
            cur.execute(op, vals)
        if not self.finish_db():
            return False
        return True

    def read_tag(self):
        '''
        load the tags in database
        '''
        if not self.init_db():
            return False
        cur=self.conn.cursor()
        op="SELECT content FROM tags WHERE type==%d"%self.dbt
        cur.execute(op)
        rets=[ret[0] for ret in cur]
        if len(ret)==0:
            return False
        self.result=[self.uni2utf8(ret) for ret in rets]
        return True

    def get_tag(self):
        '''
        获得所有标签，没有返回Boolean
        '''
        tag_url=self.get_domain()+'tag/'
        h=httplib2.Http()
        headers=self.get_headers()
        try:
            resp, tag_html=h.request(tag_url, "GET", headers=headers)
        except (httplib2.ServerNotFoundError), e:
            print e
            return False
        self.set_html(tag_html)
        return True

    def parse_tag(self):
        '''
        获得页面所有标签，保存标签列表
        '''
        tag_re=r'<td><a href="\./(?P<tag>.+?)">(?P=tag)</a>'
        tag_pattern=re.compile(tag_re, re.S)
        tag_res=tag_pattern.findall(self.get_html())
        self.msg=len(tag_res)
        self.result=tag_res
        if not self.result:
            return False
        return True

    def localstart(self):
        if not self.read_tag():
            return self.netstart(True)
        else:
            return True

    def netstart(self, save=True):
        if not self.get_tag():
            return False
        if not self.parse_tag():
            return False
        if save:
            return self.save_tag()
        return True

if __name__=='__main__':
    r=RobotTag(0)
    print r.netstart(True)
