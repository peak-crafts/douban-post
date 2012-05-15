# -*- coding: utf-8 -*-
import re
import random

class RobotBase(object):
    def __init__(self, db_type=0):
        db=['movie', 'music', 'book']
        if db_type not in [0, 1, 2]:
            db_type=0
        self.db_type=db[db_type]
        self.dbt=db_type

#对内容提取机器人的原型
class RobotParseBase(RobotBase):
    def __init__(self, db_type=0, ids_path=r'save'):
        RobotBase.__init__(self, db_type)
        self.__html=str()
        self.__ids_path=ids_path+r'\\'

    def get_headers(self):
        return {'Cookie':'bid="d%dn%02dFuFa%dg";'%( random.randint(0, 9),
                                                    random.randint(0, 99),
                                                    random.randint(0, 9))}
    def get_domain(self):
        return r'http://%s.douban.com/'%self.db_type

    def url_encode(self, content):
        return repr(content).replace(r'\x', '%')[1:-1]#这里[1:-1]去引号的
        #return url.replace(r'\x', '%')#[1:-1]

    def set_html(self, html):
        self.__html=html

    def get_html(self):
        return self.__html

    def set_idpath(self, name):
        self.__ids_path=name+r'\\'

    def get_idpath(self):
        return self.__ids_path
