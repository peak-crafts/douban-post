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
        for tag in self.tag:
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
        op="SELECT content, tid FROM tags WHERE type==%d"%self.dbt
        cur.execute(op)
        rets=[(ret[0], ret[1]) for ret in cur]
        if len(rets)==0:
            return False
        self.result=[(self.uni2utf8(ret[0]), ret[1]) for ret in rets]
        self.finish_db()
        return True

    def get_tag(self):
        '''
        get the html of tags
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
        self.tag=tag_res
        if not self.tag:
            return False
        return True

    def load_tags(self):
        if not self.read_tag():
            if not self.downloads():
                return False
            if not self.read_tag():
                return False
        return True

    def downloads(self):
        if not self.get_tag():
            return False
        if not self.parse_tag():
            return False
        return self.save_tag()

if __name__=='__main__':
    r=RobotTag(2)
    print r.load_tags()
    print r.result
