# -*- coding: UTF-8 -*-
from RobotTag import RobotTag
from RobotList import RobotList
from RobotSid import RobotSid
from RobotBase import RobotBase
import pickle
import os
import random

class RobotControl(RobotBase):
    def __init__(self, db_type=0):
        RobotBase.__init__(self, db_type)
        self.msg=str()

    def read_tag(self):
        r_tag=RobotTag(self.dbt)
        if not r_tag.load_tags():
            return False
        self.tags=r_tag.result
        return True

    def read_list(self, tid):
        r_list=RobotList(self.dbt)
        if not r_list.load_lists(tid):
            return False
        self.lists=r_list.result
        return True

    def update_done(self, tid, interest=4):
        r_sid=RobotSid(self.dbt)
        if self.todo_start==self.done_start:
            self.msg='此类别已经完成'
            return 2
        else:
            if not r_sid.start(self.lists[self.done_start][0], interest):
                return 0
            self.msg=r_sid.get_iwanna()+'『%s』'%self.lists[self.done_start][1]
            self.msg+='(还有 %d)'%(self.todo_start-self.done_start-1)
            self.done_start+=1
        return 1
        
    def start(self, tid, ndone=10, interest=4):
        if not self.read_list(tid):
            return False
        self.todo_start=len(self.lists)
        self.done_start=0
        for i in range(ndone):
            ret1=self.update_done(tid, interest)
            if ret1==0:
                return False
            elif ret1==2:
                print (self.msg)
                break
            else:
                print (self.msg)
        return True

def get_tid(dbt):    
    r_control=RobotControl(dbt)
    #done_start=self.profile[self.dbt][tid][1]
    if not r_control.read_tag():
        return False
    tag_res=r_control.tags
    msg=str()
    for i, name in enumerate(tag_res):
        msg+='%d.%s '%(i+1, name[0])
        if (i+1)%6 ==0:
            msg+='\n'
    msg+='\n这里面的第几个：'
    ret=input(msg)
    ret-=1
    return tag_res[ret][1]

def get_num():
    return input('要进行多少次呢：')

def get_interest(t):
    iwanna=[('看过', '想看', '正在看'),
            ('听过', '想听', '正在听'),
            ('读过', '想读', '正在读'),]
    msg='要怎么进行，1.%s 2.%s 3.%s 4.随意：'%(iwanna[t][0],
                                    iwanna[t][1],
                                    iwanna[t][2])
    ret= input(msg)
    return ret

def main():
    while (True):
        dbt=input('现在想做什么呢：1.看电影 2.听音乐 3.阅读 4.休息了：')
        dbt-=1
        if dbt not in [0, 1, 2]:
            break
        tid=get_tid(dbt)
        num=get_num()
        inter=get_interest(dbt)

        r_p=RobotControl(dbt)
        if not r_p.start(tid, num, inter):
            continue

if __name__=='__main__':
    main()
