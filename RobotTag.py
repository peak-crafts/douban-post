# -*- coding: utf-8 -*-
import re
from RobotBase import RobotParseBase
import httplib2
import pickle

class RobotTag(RobotParseBase):
    def __init__(self, db_type=0):
        RobotParseBase.__init__(self, db_type)
        self.result=[]

    def save_tag(self):
        '''
        保存更新的tag到文件__procees_file, 失败返回[]
        '''        
        try:
            tag_f=open(self.db_type+'.dat', 'wb')
        except IOError, e:
            #print e
            return False
        pickle.dump(self.result, tag_f)
        tag_f.close()
        return True

    def read_tag(self):
        '''
        读取tag文件
        '''
        try:
            tag_f=open(self.db_type+'.dat', 'rb')
        except IOError, e:
            #print e
            return False
        ret_tag=pickle.load(tag_f)
        tag_f.close()
        self.result=ret_tag
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

    def netstart(self, save=False):
        if not self.get_tag():
            return False
        if not self.parse_tag():
            return False
        if save:
            return self.save_tag()
        return True

if __name__=='__main__':
    r=RobotTag(0)
    print r.localstart()
