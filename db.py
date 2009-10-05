#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import join,exists
from sqlite3 import dbapi2 as sqlite
from mod_python import apache,util
from string import replace

# GLOBAL VARIABLES
BASE=join('/','home','tom','sf')
DBNAME=join(BASE,'new.db')


def opendb(name=DBNAME):
    if not exists(name):
        return 'Give me something, man!'
    else:
        conn=sqlite.connect(name)
        curs=conn.cursor()
        return conn,curs

def filecontent(filename,base=BASE):
        """ returns the content of a filename"""
        f=open(join(base,filename))
        content=f.read()
        f.close()
        return content

def rescon(ty):
    if ty==0: return "None"
    elif ty==1: return "Only talk"
    elif ty==2: return "Only poster"
    elif ty==3: return "If possible talk, poster otherwise"
    elif ty==4: return "Practical demonstration"
    elif ty==5: return "Discussion session"
    else: return "Unknown value"

def resacc(ty):
    if ty==0: return "Single"
    elif ty==1: return "Shared double"
    elif ty==2: return "Not at OAC"
    elif ty==3: return "See comment"
    else: return "Unknown value"

def restud(ty):
    if ty==0: return "No"
    elif ty==1: return "Yes"
    else: return "Unknown value"

def resoac(ty):
    if ty==0: return "Yes"
    elif ty==1: return "No"
    else: return ""

def getconlinksbyid(pid,curs):
    result=''
    all=curs.execute('SELECT id,pid FROM contr WHERE pid==%s'%pid).fetchall()
    for id,pid in all:
        result+='<a href="/contribs#anch%s">%s</a>, '%(id,id)
    return result.strip(' ,')
        
    

def listpersons(curs):
    result='<table border="1"><tr><td>ID </td><td>Name </td><td>Email, Affiliation</td><td>Contrib</td><td>Student? </td><td>Accom. </td><td>to pay </td><td> has payed</td><td>Comment</td></tr>'
    wanted='id,fname,lname,email,affil,student,accom,hastopay,haspayed,comment'
    all=curs.execute('SELECT %s FROM pers'%wanted).fetchall()
    for id,fname,lname,email,affil,student,accom,hastopay,haspayed,comment in all:
        result+='<tr><td><a href="/p%s">%s</a> </td><td>%s %s</td><td>%s, %s</td><td>%s </td><td>%s </td><td>%s </td><td>%s </td><td>%s </td><td>%s</td></tr>'%(id,id,fname,lname,email,affil,getconlinksbyid(id,curs),restud(student),resacc(accom),hastopay,haspayed,comment)
    result+='</table>'
    return result.encode('utf-8')

def listtravels(curs):
    result='<table border="1"><tr><td>ID </td><td>Name </td><td>Registration comment</td><td>Travel comment</td><td>Airport</td><td>Arrival</td><td>Departure</td><td>Accomodation</td><td>All nights at OAC</td></tr>'
    wanted='id,fname,lname,comment,travelcomm,airport,arrday,arrtime,arrflight,depday,deptime,deplight,accom,notoac'
    all=curs.execute('SELECT %s FROM pers'%wanted).fetchall()
    for id,fname,lname,comment,travelcomm,airport,arrday,arrtime,arrflight,depday,deptime,deplight,accom,notoac in all:
        data=[id,fname,lname,comment,travelcomm,airport,arrday,arrtime,arrflight,depday,deptime,deplight,resacc(accom),resoac(notoac)]
        #[ s.replace('None', '') for s in data ]
        result+=replace('<tr><td>%s</td><td>%s %s</td><td>%s</td><td>%s</td><td>%s</td><td>%s, %s, %s </td><td>%s, %s, %s</td><td>%s </td><td>%s </td></tr>'%tuple(data),'None','')
    result+='</table>'
    return result.encode('utf-8')

def listcontribs(curs):
    result='<p>'
    wanted='id,pid,type,title,abstract'
    all=curs.execute('SELECT %s FROM contr'%wanted).fetchall()
    for id,pid,type,title,abstract in all:
        fname,lname,affil=curs.execute('SELECT %s FROM pers WHERE id==%s'%('fname,lname,affil',pid)).fetchone()
        result+='<ul><li><strong><a name="anch%s"/>ID:</strong> <a href="/c%s">%s</a>, <strong>PID:</strong> <a href="/p%s">%s</a></li><li><strong>Name/Affiliation:</strong> %s %s, %s</li><li><strong>Type:</strong> %s</li><li><strong>Title:</strong> %s</li><li><strong>Abstract:</strong><br>%s</li></ul><hr/>'%(id,id,id,pid,pid,fname,lname,affil,rescon(type),title,abstract)
    result+='</p>'
    result+='<br/>'*50
    return result.encode('utf-8')

def listcontribsshort(curs):
    result='<p>'
    wanted='id,pid,type,title,abstract'
    all=curs.execute('SELECT %s FROM contr'%wanted).fetchall()
    for id,pid,type,title,abstract in all:
        fname,lname,affil=curs.execute('SELECT %s FROM pers WHERE id==%s'%('fname,lname,affil',pid)).fetchone()
        result+='<ul><li><strong>ID:</strong> %s</li><li><strong>Name, Affiliation:</strong> %s %s, %s</li><li><strong>Type:</strong> %s</li><li><strong>Title:</strong> %s</li><li><strong>Abstract:</strong><br>%s</li></ul><hr/>'%(id,fname,lname,affil,rescon(type),title,abstract)
    result+='</p>'
    result+='<br/>'*50
    return result.encode('utf-8')

def editperson(number,curs):
    result='<p>Editing person with ID: %s<p/>'%number
    result+='<p><FORM ACTION="/epc" METHOD="POST">'
    wanted='id,fname,lname,email,affil,addr,student,paymeth,accom,hastopay,haspayed,comment'
    wantsplit=wanted.split(',')
    curs.execute('SELECT %s FROM pers WHERE id==%s'%(wanted,number))
    for i,cont in enumerate(curs.fetchone()):
        result+='%s<br/><textarea cols="60" rows="6" name="%s">%s</textarea><br/><br/>'%(wantsplit[i],wantsplit[i],cont)
    result+='<INPUT TYPE="submit" VALUE="SEND" NAME="send">'
    result+='</p>'
    return result.encode('utf-8')

def epc(form,curs):
    wanted='id,fname,lname,email,affil,addr,student,paymeth,accom,hastopay,haspayed,comment'
    wantsplit=wanted.split(',')
    for i in wantsplit[1:]:
        curs.execute('UPDATE pers SET %s="%s" WHERE id==%s'%(i,form.getfirst(i,''),form.getfirst('id')))
    return 'Editing done. Return to <br/>'+startpage()

def editcontr(number,curs):
    result='<p>Editing contribution with ID: %s<p/>'%number
    result+='<p><FORM ACTION="/ecc" METHOD="POST">'
    wanted='id,pid,type,title,abstract'
    wantsplit=wanted.split(',')
    curs.execute('SELECT %s FROM contr WHERE id==%s'%(wanted,number))
    for i,cont in enumerate(curs.fetchone()):
        result+='%s<br/><textarea cols="60" rows="6" name="%s">%s</textarea><br/><br/>'%(wantsplit[i],wantsplit[i],cont)
    result+='<INPUT TYPE="submit" VALUE="SEND" NAME="send">'
    result+='</p>'
    return result.encode('utf-8')

def ecc(form,curs):
    wanted='id,pid,abstract,title'
    wantsplit=wanted.split(',')
    for i in wantsplit[1:]:
        curs.execute('UPDATE contr SET %s="%s" WHERE id==%s'%(i,form.getfirst(i,''),form.getfirst('id')))
    return 'Editing done. Return to <br/>'+startpage()

def newpers(curs):
    return 'adding person not yet implemented here, they are inserted automatically when they register'

def newcontr(curs):
    result=listpersons(curs)
    result+='<p>Adding a contribution. Make sure you put in the right ID for the person and numerical value (1-3) for the type!</p>'
    result+='<p><FORM ACTION="/ncc" METHOD="POST">'
    wanted='pid,type,title,abstract,filename'
    wantsplit=wanted.split(',')
    for i in wantsplit:
        result+='%s<br/><textarea cols="60" rows="6" name="%s"></textarea><br/><br/>'%(i,i)
    result+='<INPUT TYPE="submit" VALUE="SEND" NAME="send">'
    result+='</p>'
    return result

def ncc(form,curs):
    wanted='pid,type,title,abstract,filename'
    wantsplit=wanted.split(',')
    curs.execute('INSERT INTO contr VALUES (null, ?, ?, ?, ?, ?)',tuple([form.getfirst(i,'') for i in wantsplit]))
    return 'Contribution added. Return to <br/>'+startpage()


def startpage():
    return """<ul>
    <li><a href="/persons">persons</a></li>
    <li><a href="/contribs">contributions</a></li>
    <li><a href="/travels">travel data</a></li>
    <li><a href="/newc">new contribution</a></li>
    <li><a href="/newp">new person</a></li>
    <li><a href="/">...</a></li>
    </ul>"""

def notallowed():
    return 'You are not allowed to view this page. (You can ask Thomas to make changes or to give you access.)'

def testadmin(req):
    if req.user=='admin': return True
    else: return False
    #return True

def testsfdg(req):
    if (req.user=='admin') or (req.user=='sfdg'): return True
    else: return False


def handler(req):
        """ the real work is done here """
        
        req.content_type = "text/html"
        form=util.FieldStorage(req)
        req.write(filecontent('head'))

        conn,curs=opendb()

        wanted=req.uri[1:]
        if wanted == '': 
	    if testsfdg(req): req.write(startpage())
	    else: req.write(notallowed())

        elif wanted == 'persons':
            if testsfdg(req): req.write(listpersons(curs))
            else: req.write(notallowed())

        elif wanted == 'travels':
            if testsfdg(req): req.write(listtravels(curs))
            else: req.write(notallowed())

        elif wanted == 'contribs':
            if testsfdg(req): req.write(listcontribs(curs))
            else: req.write(notallowed())

        elif wanted == 'contributions':
            req.write(listcontribsshort(curs))

        elif wanted in ['c'+i for i in map(str,range(100))]:
            if testadmin(req): req.write(editcontr(wanted[1:],curs))
            else: req.write(notallowed())

        elif wanted in ['p'+i for i in map(str,range(100))]:
            if testadmin(req): req.write(editperson(wanted[1:],curs))
            else: req.write(notallowed())

        elif wanted == 'epc':
            if testadmin(req): req.write(epc(form,curs))
            else: req.write(notallowed())

        elif wanted == 'ecc':
            if testadmin(req): req.write(ecc(form,curs))
            else: req.write(notallowed())

        elif wanted == 'newp':
            if testadmin(req): req.write(newpers(curs))
            else: req.write(notallowed())

        elif wanted == 'newc':
            if testadmin(req): req.write(newcontr(curs))
            else: req.write(notallowed())

        elif wanted == 'ncc':
            if testadmin(req): req.write(ncc(form,curs))
            else: req.write(notallowed())

        else:
            req.write('Don\'t know what to do with %s'%req.uri)

        conn.commit()
        conn.close()

        req.write(filecontent('foot'))
        return apache.OK
