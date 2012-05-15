# -*- coding: UTF-8 -*-
from RobotTag import RobotTag
from RobotList import RobotList
from RobotSid import RobotSid
from RobotBase import RobotBase
import pickle
import os
import random

class RobotProfile(RobotBase):
    def __init__(self, db_type=0, profile_name=r'profile.dat'):
        RobotBase.__init__(self, db_type)
        self.profile_name=profile_name
        self.profile=[[],
                      [],
                      []]
        self.msg=str()

    def read_profile(self):
        try:
            f=open(self.profile_name, 'rb')
            self.profile=pickle.load(f)
        except (IOError, EOFError), e:
            #print e
            return False
        f.close()
        return True

    def save_profile(self):
        try:
            f=open(self.profile_name, 'wb')
            pickle.dump(self.profile, f)
        except (IOError, EOFError), e:
            #print e
            return False
        f.close()
        return True

    def initial_tag(self, local_first=True):
        for i in [0, 1, 2]:
            r_tag=RobotTag(i)
            temp=list()
            if local_first:
                if not r_tag.localstart():
                    return False
            else:
                if not r_tag.netstart():
                    return False
            tag_res=r_tag.result
            for j in range(len(tag_res)):
                temp.append((0, 0))
            self.profile[i].extend(temp)
        return self.save_profile()

    def read_todo(self, tid=0, local_first=True):
        r_tag=RobotTag(self.dbt)
        r_list=RobotList(self.dbt)
        #done_start=self.profile[self.dbt][tid][1]
        if local_first:
            if not r_tag.localstart():
                return False
        else:
            if not r_tag.netstart():
                return False
        tag_res=r_tag.result
        tag_name=tag_res[tid]
        if local_first:
            if not r_list.localstart(tag_name):
                return False
        else:
            if not r_list.netstart(tag_name):
                return False
        #self.profile[self.dbt][tid]=(r_list.count, done_start)
        self.lists=r_list.result
        return True
        

    def update_todo(self, tid=0):
        if self.profile[self.dbt][tid][0]==0:
            done_start=self.profile[self.dbt][tid][1]
            self.profile[self.dbt][tid]=(len(self.lists), done_start)
        else:
            return True
        return self.save_profile()

    def update_done(self, tid=0, interest=4):
        r_sid=RobotSid(self.dbt)
        todo_start=self.profile[self.dbt][tid][0]
        done_start=self.profile[self.dbt][tid][1]
        if todo_start==done_start:
            self.msg='此类别已经完成'
            return 2
        else:
            if not r_sid.start(self.lists[done_start][0], interest):
                return 0
            self.msg=r_sid.get_iwanna()+'『%s』'%self.lists[done_start][1]
            self.msg+='(还有 %d)'%(todo_start-done_start-1)
            #self.msg=self.msg.encode('utf-8')
            done_start+=1
            self.profile[self.dbt][tid]=(todo_start, done_start)
            if not self.save_profile():
                return 0
            else:
                return 1
        
    def start(self, tid=0, ndone=10, interest=4):
        if not self.read_profile():
            print transcode('重新开始记录')
            self.initial_tag()
        if not self.read_todo(tid):
                return False
        if not self.update_todo(tid):
                return False
        for i in range(ndone):
            ret1=self.update_done(tid, interest)
            if ret1==0:
                return False
            elif ret1==2:
                print transcode(self.msg)
                break
            else:
                print transcode(self.msg)
        return True

def get_tid(dbt):    
    r_tag=RobotTag(dbt)
    #done_start=self.profile[self.dbt][tid][1]
    if not r_tag.localstart():
        return False
    tag_res=r_tag.result
    msg=str()
    for i, name in enumerate(tag_res):
        msg+='%d.%s '%(i+1, name)
        if (i+1)%6 ==0:
            msg+='\n'
    msg+='\n这里面的第几个：'
    ret=input(transcode(msg))
    ret-=1
    return ret

def transcode(string):
    return u2c(string)

def u2c(string):
    return string.decode('utf-8').encode('cp936')

def get_num():
    return input(transcode('要进行多少次呢：'))

def get_interest(t):
    iwanna=[('看过', '想看', '正在看'),
            ('听过', '想听', '正在听'),
            ('读过', '想读', '正在读'),]
    msg='要怎么进行，1.%s 2.%s 3.%s 4.随意：'%(iwanna[t][0],
                                    iwanna[t][1],
                                    iwanna[t][2])
    ret= input(transcode(msg))

def main():
    while (True):
        dbt=input(transcode('现在想做什么呢：1.看电影 2.听音乐 3.阅读 4.休息了：'))
        dbt-=1
        if dbt not in [0, 1, 2]:
            break
        r_p=RobotProfile(dbt)
        tid=get_tid(dbt)
        num=get_num()
        inter=get_interest(dbt)
        if not r_p.start(tid, num, inter):
            continue

if __name__=='__main__':
    main()
