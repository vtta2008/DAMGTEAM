# -*- coding: utf-8 -*-
"""
Script Name: ultilitis_user.py
Author: Do Trinh/Jimmy - 3D artist.

Description:
    This script is main file to create, modify and/or query database
    For now, database is offline, but it will be online soon, we going to work together via a server.

"""

# -------------------------------------------------------------------------------------------------------------
""" About Plt """

__appname__ = "Pipeline Tool"
__module__ = "Plt"
__version__ = "13.0.1"
__organization__ = "DAMG team"
__website__ = "www.dot.damgteam.com"
__email__ = "dot@damgteam.com"
__author__ = "Trinh Do, a.k.a: Jimmy"
__root__ = "PLT_RT"
__db__ = "PLT_DB"
__st__ = "PLT_ST"

# -------------------------------------------------------------------------------------------------------------
""" Import modules """

# Python
import logging
import os
import sqlite3 as lite


# -------------------------------------------------------------------------------------------------------------
""" Configure the current level to make it disable certain log """

logPth = os.path.join(os.getenv(__root__), 'appData', 'logs', 'utils_sql.log')
logger = logging.getLogger('utils_sql')
handler = logging.FileHandler('utils_sql')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# -------------------------------------------------------------------------------------------------------------
""" Plt tools """

from utilities import utils as func
from utilities import variables as var

# -------------------------------------------------------------------------------------------------------------
""" Variables """

dataPth = var.DB_PATH
conn = lite.connect(dataPth)
c = conn.cursor()

USERCLASSDATA = ['Tester, DemoUser, NormalUser', 'Artist', 'Instructor', 'CEO', 'Supervisor', 'Leader']

# -------------------------------------------------------------------------------------------------------------
""" Delete Data """

def remove_all_data_table(tableName):
    # Delete old data first
    c.execute("SELECT * FROM {tableName}".format(tableName=tableName))
    c.fetchall()
    c.execute("DELETE FROM {tableName}".format(tableName=tableName))
    conn.commit()
    insert_timeLog('Clean data in table: %s' % tableName)

# -------------------------------------------------------------------------------------------------------------
""" Create Dataset Table """

def username( username):
    c.execute("CREATE TABLE IF NOT EXISTS {username} (password TEXT, firstname TEXT, lastname TEXT, title TEXT,"
    "email TEXT, phone TEXT, address1 TEXT, address2 TEXT, postal TEXT, city TEXT, country TEXT)".format(username=username))
    logger.info("table %s created" % username)
    conn.commit()

def userData(self):
    c.execute("CREATE TABLE IF NOT EXISTS userData (username TEXT, date_create TEXT, unix TEXT, token TEXT, "
              "question1 TEXT, answer1 TEXT, question2 TEXT, answer2 TEXT)")
    logger.info("table userData created")
    conn.commit()

def userSetting(self):
    c.execute("CREATE TABLE IF NOT EXISTS userSetting (username TEXT, showToolbar TXT, avatar TEXT)")
    logger.info("table userSetting created")
    conn.commit()

def userLog(self):
    c.execute("CREATE TABLE IF NOT EXISTS userLog (username TEXT, date TEXT, login TEXT, logout TEXT)")
    logger.info("table userLog created")
    conn.commit()

def userClass(self):
    c.execute("CREATE TABLE IF NOT EXISTS userClass (username TEXT, class TEXT, status TEXT)")
    logger.info("table userClass created")
    conn.commit()

def curUser(self):
    c.execute("CREATE TABLE IF NOT EXISTS curUser (username TEXT, auto_login TEXT)")
    logger.info("table curUser created")
    conn.commit()

def timeLog(self):
    c.execute("CREATE TABLE IF NOT EXISTS timeLog (dateTime TEXT , username TEXT, eventlog TEXT)")
    logger.info("table timeLog created")
    conn.commit()

def tokenID(self):
    c.execute("CREATE TABLE IF NOT EXISTS tokenID (token TEXT, username TEXT, timelog TEXT, productID TEXT, ip TEXT, "
              "city TEXT, country TEXT)")
    logger.info("table tokenID created")
    conn.commit()

def pcID(self):
    c.execute("CREATE TABLE IF NOT EXISTS pcID (token TEXT, productID TEXT, os TEXT, pcUser TEXT, python TEXT)")
    logger.info("table pcID created")
    conn.commit()

# -------------------------------------------------------------------------------------------------------------
""" For production """

def prjLst(self):
    c.execute("CREATE TABLE IF NOT EXISTS prjLst (status TEXT, projName TEXT, start TEXT, end TEXT )")
    logger.info("table prjLst created")
    conn.commit()

def prjCrew(self):
    c.execute("CREATE TABLE IF NOT EXISTS projCrew (projID TEXT, username TEXT, position TEXT)")
    logger.info("table projCrew created")
    conn.commit()

def prjTaskID( projName):
    c.execute("CREATE TABLE IF NOT EXISTS {projName} (projStage TEXT, assetID TEXT, shotID TEXT, taskID TEXT, "
              "status TEXT, assign TEXT, start TEXT, end TEXT)".format(projName=projName))
    logger.info("table %s created" % projName)
    conn.commit()

# -------------------------------------------------------------------------------------------------------------
""" Configuration """

def pltConfig(self):
    c.execute("CREATE TABLE IF NOT EXISTS pltConfig (appName TEXT, version VARCHAR(20), exePth VARCHAR(20))")
    logger.info("table plt created")
    conn.commit()

def tableConfig(self):
    c.execute("CREATE TABLE IF NOT EXISTS tableConfig (tableName TEXT, columnList TEXT, datetimeLog TEXT)")
    logger.info("table tableConfig created")
    conn.commit()

def dataConfig(self):
    c.execute("CREATE TABLE IF NOT EXISTS dataConfig (setup TEXT, account TEXT, message TEXT, name TEXT, format TEXT)")
    logger.info("table dataConfig created")
    conn.commit()

# -------------------------------------------------------------------------------------------------------------
""" Query Data """

def query_tableLst():
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    return [str(t[0]) for t in c.fetchall()]

def query_userData():
    c.execute("SELECT * FROM userData")
    data = [r for r in c.fetchall()]
    data = (data[0])[1]
    return data

def query_columnLst(tableName):
    c.execute("SELECT * FROM {tn}".format(tn=tableName))
    return [str(m[0]) for m in c.description]

def query_userLst():
    c.execute("SELECT username FROM AccountUser")
    data = [str(r[0]) for r in c.fetchall()]
    return data

def query_unixLst():
    c.execute("SELECT unix FROM userData")
    data = [str(r[0]) for r in c.fetchall()]
    return data

def query_tokenLst():
    c.execute("SELECT token FROM TokenLog")
    data = [str(r[0]) for r in c.fetchall()]
    return data

def query_userTokenLst():
    c.execute("SELECT token FROM AccountUser")
    data = [str(r[0]) for r in c.fetchall()]
    return data

def query_appIDLst():
    c.execute("SELECT productID FROM TokenLog")
    data = [str(t[0]) for t in c.fetchall()]
    return data

def query_curUser():
    c.execute("SELECT * FROM curUser")
    data = c.fetchall()
    if len(data) == 0:
        user = [" ", "False"]
    else:
        user = [str(p) for p in list(data[0])]
    return user

def query_userClass(username):
    c.execute("SELECT * FROM userClass")
    rows = c.fetchall()
    row = rows[0]
    if username == row[0]:
        userClass = str(row[1]).split("'")[0]
    else:
        pass
    return userClass

userClass = query_userClass('vtta2008')

def query_userStatus(username):
    userData = query_userClass(username)
    status = userData[-1]
    return status

def query_securityQts(username):
    userData = query_userData(username)
    question1 = userData[-3]
    question2 = userData[-2]
    return question1, question2

def query_passwordLst(username):
    pass

# -------------------------------------------------------------------------------------------------------------
""" Check Data """

def check_account( name, typeName='username'):
    if typeName == 'unix':
        checkList = query_unixLst()
    elif typeName == 'token':
        checkList = query_tokenLst()
    else:
        checkList = query_userLst()

    if name in checkList:
        return True
    else:
        return False

def check_localPC( productID):
    idList = query_appIDLst()
    if idList is None or idList == []:
        return False
    else:
        if productID in idList:
            return True
        else:
            return False

def check_sysConfig(username):
    info = func.get_local_pc()
    productID = info['Product ID']
    check = check_localPC(productID)
    if check:
        token = query_tokenLst()
        update_sysInfo(token, info)
    else:
        token = func.get_token()
        insert_tokenID(username, token, productID)
    return productID

def check_pw_match(username, password):
    usernameLst = query_userLst()
    passwordLst = query_passwordLst()
    passCheck = passwordLst[usernameLst.index(username)]
    if password == passCheck:
        check = True
    else:
        check = False
    return check

# -------------------------------------------------------------------------------------------------------------
""" Modify Data """

def insert_userTable(data):
    username = data[0]
    c.execute("INSERT INTO {username} (password, firstname, lastname, title, email, phone, address1, address2, "
              "postal, city, country) VALUES (?,?,?,?,?,?,?,?,?,?,?)".format(username = username),
        (data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]))
    conn.commit()

def insert_userData(data):
    c.execute("INSERT INTO userData (username, dateCreate, unix, token, question1, answer1, question2, answer2) "
              "VALUES (?,?,?,?,?,?,?,?)", (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))
    conn.commit()

def insert_tokenID(data):
    c.execute("INSERT INTO token (token, username, productID, ip, city, country) VALUES (?,?,?,?,?,?)",
              (data[0], data[1], data[2], data[3], data[4], data[5]))
    conn.commit()

def insert_timeLog(eventlog):
    username = query_curUser()[0]
    datetimeLog = func.get_datetime()
    c.execute("INSERT INTO TimeLog (dateTime, username, eventLog) VALUES (?,?,?)",
              (datetimeLog, username, eventlog))
    conn.commit()
    return True

def insert_pcid(username, token, info):
    datetimeLog = func.get_datetime()
    productID = info["Product ID"]
    OS = info['os']
    pcUser = info['pcUser']
    python = info['python']
    c.execute("INSERT INTO pcid (token, productid, os, pcuser, python) VALUES (?,?,?,?,?)",
              (token, username, productID, OS, pcUser, python, datetimeLog))
    conn.commit()

def insert_userClass(data):
    c.execute("INSERT INTO userClass (username, class, status) VALUES (?,?,?)", (data[0], data[1], data[2]))
    conn.commit()

def insert_pcID(data):
    c.execute("INSERT INTO pcid (token, productID, os, pcUser, python) VALUES (?,?,?,?,?)",
              (data[0], data[1], data[2], data[3], data[4]))
    conn.commit()

def insert_curUser(username):
    c.execute("INSERT INTO curUser (username) VALUES (?)", (username,))

def insert_update_curUser(username, rememberLogin):
    c.execute("SELECT * FROM CurrentUser")
    data = c.fetchall()
    c.execute("DELETE FROM CurrentUser")
    c.execute("INSERT INTO CurrentUser (username,rememberLogin) VALUES (?,?)",(username, rememberLogin))
    conn.commit()

def insert_update_rememberLogin(token, newValue):
    c.execute("SELECT * FROM TokenLog")
    c.fetchall()
    c.execute("UPDATE TokenLog SET rememberLogin = (?) WHERE token = (?)", (newValue, token))
    conn.commit()
    insert_timeLog('Update New User Login')

def update_sysInfo(token, info):
    c.execute("SELECT * FROM ProductID")
    productID = info["Product ID"]
    os = info['os']
    pcUser = info['pcUser']
    python = info['python']
    c.execute("UPDATE pcid SET token=(?), productID=(?), os=(?), pcUser=(?), python=(?)",
              (token, productID, os, pcUser, python))
    conn.commit()

def update_tableLst():
    c.execute("SELECT * FROM TableContent")
    data = c.fetchall()
    c.execute("DELETE FROM TableContent")
    tableLst = query_tableLst()

    if 'UserClassDB' in tableLst:
        tableLst.remove('UserClassDB')

    for tableName in tableLst:
        cll = query_columnLst(tableName)
        columnContent = ""
        for column in cll:
            columnContent = columnContent + column + "||"
        datetimeLog = func.get_datetime()
        c.execute("INSERT INTO TableContent (tableName, columnList, datetimeLog) VALUES (?,?,?)",
                  (tableName, columnContent, datetimeLog))
    conn.commit()
    event = 'Update table all content'
    insert_timeLog(event) 

def update_password(unix, new_password):
    c.execute("SELECT * FROM AccountUser")
    rows = c.fetchall()
    c.execute("UPDATE AccountUser Set password = (?) WHERE unix = (?)", (new_password, unix))
    conn.commit()
    insert_timeLog('Changed password')

# -------------------------------------------------------------------------------------------------------------