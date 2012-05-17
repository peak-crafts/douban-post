# -*- coding: utf-8 -*-
import re
import random
import sqlite3

class RobotBase(object):
    def __init__(self, db_type=0):
        db=['movie', 'music', 'book']
        if db_type not in [0, 1, 2]:
            db_type=0
        self.db_type=db[db_type]
        self.dbt=db_type

#对内容提取机器人的原型
class RobotParseBase(RobotBase):
    def __init__(self, db_type=0, db_name='douban.db'):
        RobotBase.__init__(self, db_type)
        self.__html=str()
        self.db_name=db_name
        self.db_conn=None

    def get_headers(self):
        return {'Cookie':'bid="d%dn%02dFuFa%dg";'%( random.randint(0, 9),
                                                    random.randint(0, 99),
                                                    random.randint(0, 9))}
    def get_domain(self):
        return r'http://%s.douban.com/'%self.db_type

    def url_encode(self, content):
        return repr(content).replace(r'\x', '%')[1:-1]#这里[1:-1]去引号的
        #return url.replace(r'\x', '%')#[1:-1]

    def utf82uni(self, content):
        return content.decode('utf-8')

    def uni2utf8(self, content):
        return content.encode("utf-8")

    def set_html(self, html):
        self.__html=html

    def get_html(self):
        return self.__html

    def create_db(self):
        try:
            conn=sqlite3.connect(self.db_name)
        except sqlite3.DatabaseError, e:
            print e
            return False
        curs=conn.cursor()
        op='''SELECT name 
            FROM sqlite_master
            WHERE type='table' AND name='lists'
        '''
        curs.execute(op)
        res=curs.fetchall()
        if res:
            return True
        op='''CREATE TABLE tags(
            tid     INTEGER PRIMARY KEY,
            content TEXT,
            type    INTEGER
        )
        '''
        curs.execute(op)
        op='''CREATE TABLE lists(
            id      INTEGER PRIMARY KEY,
            sid     INTEGER,
            tid     INTEGER,
            done    INTEGER,
            tittle  TEXT
        )
        '''
        curs.execute(op)
        op='''CREATE TABLE subjects(
            id      INTEGER PRIMARY KEY,
            sid     INTEGER,
            rate    INTEGER,
            tags    TEXT,
            comment TEXT
        )
        '''
        curs.execute(op)
        curs.close()
        conn.close()
        return True

    def init_db(self):
        try:
            self.conn=sqlite3.connect(self.db_name)
        except sqlite3.DatabaseError, e:
            print e
            return False
        return True

    def finish_db(self):
        try :
            self.conn.commit()
            self.conn.close()
        except (), e:
            print e
            return False
        return True

if __name__=='__main__':
    rb=RobotParseBase()
    rb.create_db()
