#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import string
from os.path import join,exists
from sqlite3 import dbapi2 as sqlite
from codecs import open

# GLOBAL VARIABLES
BASE=join('/','home','tom','sf')
DBNAME=join(BASE,'new.db')
CONTRIBS=join(BASE,'contributions.txt')
NDATA=13
NTRAVEL=10
TOPAY='150'
TOPAYSTUDENT='100'

# THE CODE ITSELF
def reademails(curs,file):
    data=['']*NDATA
    count=0
    for line in file:
        if line.startswith('Date:'):
            data[0]=string.join(line.strip().split()[1:])
            continue
        if '-----' in line:
            count+=1
            continue
        if count<NDATA and count>0:
            data[count]+=line
            continue
        if 'regform_form' in line:
            data=map(string.strip,data)
            if data[6]=='0': data.append('150') # The "hastopay" field
            elif data[6]=='1': data.append('100') # for students
            else: print "Something's fishy!"; sys.exit()
            data.append('0') # This is for the "haspayed" field
            print tuple(data)
            type=data.pop(9)
            title=data.pop(9)
            abstr=data.pop(9)
            curs.execute('INSERT INTO pers VALUES (null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',tuple(data+['null']*9))
            if type != '0': curs.execute('INSERT INTO contr VALUES (null, ?, ?, ?, ?)',(curs.lastrowid,type,title,abstr))
            data=['']*NDATA
            count=0
            
def readtravel(curs,id, file):
    data=['']*NTRAVEL
    count=-1
    for line in file:
        if '-----' in line:
            count+=1
            continue
        if count<NTRAVEL and count>=0:
            data[count]+=line
            continue
        if 'itiform_form' in line:
            data=map(string.strip,data)
            name=data.pop(0)
            data+=[id]
            print data
            curs.execute('UPDATE pers SET airport = ? , arrday = ? , arrtime = ? , arrflight = ? , depday = ? , deptime = ? , deplight = ? , notoac = ? , travelcomm = ? WHERE id = ?',tuple(data))
            
            # For the next email
            data=['']*NDATA
            count=-1

        
def newdb(name=DBNAME):
    conn=sqlite.connect(name)
    curs=conn.cursor()
    curs.execute('CREATE TABLE pers (id INTEGER PRIMARY KEY, date TEXT, fname TEXT, lname TEXT, email TEXT, affil TEXT, addr TEXT, student INTEGER, paymeth INTEGER, accom INTEGER, comment TEXT, hastopay INTEGER, haspayed INTEGER)')
    curs.execute('CREATE TABLE contr (id INTEGER PRIMARY KEY, pid INTEGER, type INTEGER, title TEXT, abstract TEXT)')
    return conn,curs

def opendb(name=DBNAME):
    if not exists(name):
        return newdb(name)
    else:
        conn=sqlite.connect(name)
        curs=conn.cursor()
        return conn,curs

def table1(curs):
    print '||ID ||first name ||last name || Affiliation||Student? ||Acc || Contr||to pay || has payed ||'
    print '|||||||||||||||||| ||'
    wanted='id,fname,lname,affil,student,accom,contrib,hastopay,haspayed'
    for stuff in curs.execute('SELECT %s FROM pers'%wanted):
        print '||%s ||%s ||%s ||%s ||%s ||%s ||%s ||%s ||%s ||'%stuff

def contributions(curs):
    wanted='id,fname,lname,contrib,title,abstract'
    f=open(CONTRIBS,encoding='utf-8',mode='w')
    for id,fname,lname,contrib,title,abstract in curs.execute('SELECT %s FROM pers WHERE contrib != 0'%wanted):
        f.write('%s: %s %s\n'%(id,fname,lname))
        f.write('Type wanted: %s\n'%contrib)
        f.write('Title: %s\n'%title)
        f.write('Abstract:\n%s\n'%abstract)
        f.write('\n')

def someonepayed(curs):
    wanted='id,fname,lname,hastopay,haspayed'
    for stuff in curs.execute('SELECT %s FROM pers WHERE haspayed!=hastopay ORDER BY lname'%wanted):
        print '%s: %s %s, to pay: %s, has payed: %s'%stuff
    id=raw_input('Who has payed? ')
    if id == 'q': sys.exit()
    amount=raw_input('How much? ')
    curs.execute('UPDATE pers SET haspayed=%s WHERE id==%s'%(amount,id))

def nullpay(curs):
    wanted='id,fname,lname,hastopay,haspayed'
    for stuff in curs.execute('SELECT %s FROM pers WHERE haspayed!=hastopay ORDER BY lname'%wanted):
        print '%s: %s %s, to pay: %s, has payed: %s'%stuff
    id=raw_input('Who needs not pay? ')
    if id == 'q': sys.exit()
    curs.execute('UPDATE pers SET hastopay=0 WHERE id==%s'%id)


def main():
    try: todo=sys.argv[1]
    except:
        print "Please tell me what to do!"
        sys.exit()

    conn,curs=opendb()

    if '--reademails' in todo:
        reademails(curs,sys.stdin)
    elif '--readtravel' in todo:
        readtravel(curs,sys.argv[2],sys.stdin)
    elif '--table1' in todo:
        table1(curs)
    elif '--contribs' in todo:
        contributions(curs)
    elif '--payment' in todo:
        someonepayed(curs)
    elif '--nullpay' in todo:
        nullpay(curs)
    else:
        print "Unknown command"

    conn.commit()

if __name__=='__main__':
    main()
