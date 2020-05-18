import sqlite3
import requests
import json
import matplotlib.pyplot as plt

GprovinceID = {'北京': 11, '天津': 12, '河北': 13, '山西': 14, '内蒙古': 15,
               '辽宁': 21, '吉林': 22, '黑龙江': 23,
               '上海': 31, '江苏': 32, '浙江': 33, '安徽': 34, '福建': 35, '江西': 36, '山东': 37,
               '河南': 41, '湖北': 42, '湖南': 43, '广东': 44, '广西': 45, '海南': 46,
               '重庆': 50, '四川': 51, '贵州': 52, '云南': 53,
               '陕西': 61, '甘肃': 62, '青海': 63, '宁夏': 64, '新疆': 65}

GtypeID = {'理科': 1, '文科': 2}

schoolName = '华中科技大学'
provinceName = '湖北'
typeName = '理科'


def initDB():
    '''
    create database if not exist.
    '''
    conn = sqlite3.connect('score.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS SCHOOLID
        (ID INTEGER PRIMARY KEY autoincrement,
        NAME        TEXT    NOT NULL,
        SCHOOLID    INT    NOT NULL
        );''')
    c.execute('''CREATE TABLE IF NOT EXISTS PROVINCELINE
        (ID INTEGER PRIMARY KEY autoincrement,
        NAME        TEXT    NOT NULL,
        TYPE        INT     NOT NULL,
        DATA        TEXT    NOT NULL
        );''')
    c.execute('''CREATE TABLE IF NOT EXISTS SCHOOLLINE
        (ID INTEGER PRIMARY KEY autoincrement,
        NAME        TEXT    NOT NULL,
        PROVINCE    TEXT    NOT NULL,
        TYPE        INT     NOT NULL,
        DATA        TEXT    NOT NULL
        );''')
    print("Table created successfully")
    conn.close()


def searchSchoolID(schoolName):
    conn = sqlite3.connect('score.db')
    c = conn.cursor()
    cursor = c.execute(
        "SELECT schoolid from SCHOOLID where name='%s'" % (schoolName))
    result = cursor.fetchall()
    if len(result) == 0:
        conn.close()
        return -1
    conn.close()
    return result[0][0]


def insertSchoolID(schoolName, schoolID):
    conn = sqlite3.connect('score.db')
    c = conn.cursor()
    c.execute(
        "INSERT INTO SCHOOLID (NAME, SCHOOLID) \
      VALUES ('%s', %d)" % (schoolName, schoolID))
    conn.commit()
    conn.close()


def searchProvinceLine(provinceName, stype):
    conn = sqlite3.connect('score.db')
    c = conn.cursor()
    cursor = c.execute(
        "SELECT data from PROVINCELINE where name='%s' AND type='%s'" % (provinceName, stype))
    result = cursor.fetchall()
    if len(result) == 0:
        conn.close()
        return ""
    conn.close()
    return json.loads(result[0][0])


def searchSchoolScoreLine(schoolName, provinceName, stype):
    '''
    学校名称，省份名称，科目名称
    '''
    conn = sqlite3.connect('score.db')
    c = conn.cursor()
    cursor = c.execute(
        "SELECT data from SCHOOLLINE where name='%s' AND type='%s' AND province='%s'" % (schoolName, stype, provinceName))
    result = cursor.fetchall()
    if len(result) == 0:
        conn.close()
        return ""
    conn.close()
    return json.loads(result[0][0])


def requestSchoolID(schoolName):
    url = 'https://api.eol.cn/gkcx/api/?keyword=%s&uri=apigkcx/api/school/hotlists' % (
        schoolName)
    headers = headers = {'Accept': 'text/plain, application/json, */*',
                         'Accept - Encoding': 'gzip, deflate, br',
                         'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
                         'Connection': 'Keep-Alive',
                         'Host': 'api.eol.cn',
                         'Origin': 'https://gkcx.eol.cn',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
    result = requests.get(url, headers=headers)
    info = json.loads(result.text)
    if info['data']['numFound'] == 0:
        return -1
    schoolid = info['data']['item'][0]['school_id']
    print(schoolid)
    return schoolid


def requestProvinceScoreLine(provinceName, stype):
    '''
    request province score LINE.
    from 2014-2019.
    '''
    provinceID = GprovinceID[provinceName]
    conn = sqlite3.connect('score.db')
    c = conn.cursor()
    liA = []
    liB = []
    wenA = []
    wenB = []
    for i in range(6):
        year = 2014+i
        url = 'https://api.eol.cn/gkcx/api/?page=1&province_id=%d&size=20&uri=apidata/api/gk/score/proprovince&year=%d' % (
            provinceID, year)
        headers = headers = {'Accept': 'text/plain, application/json, */*',
                             'Accept - Encoding': 'gzip, deflate, br',
                             'Accept-Language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
                             'Connection': 'Keep-Alive',
                             'Host': 'api.eol.cn',
                             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
        result = requests.get(url, headers=headers)
        info = json.loads(result.text)
        #
        if info['code'] != "0000":
            print("search province scoreLine Error")
            return ""
        if info['data']['numFound'] == 0:
            print("search province scoreLine result Zero.")
            return ""
        for i in range(info['data']['numFound']):
            if info['data']['item'][i]['local_type_name'] == '理科':
                if info['data']['item'][i]['local_batch_name'] == '本科一批' or info['data']['item'][i]['local_batch_name'] == '本科批':
                    temp = {'year': info['data']['item'][i]['year'],
                            'score': info['data']['item'][i]['average']}
                    liA.append(temp)
                elif info['data']['item'][i]['local_batch_name'] == '本科二批':
                    temp = {'year': info['data']['item'][i]['year'],
                            'score': info['data']['item'][i]['average']}
                    liB.append(temp)
                    break
            elif info['data']['item'][i]['local_type_name'] == '文科':
                if info['data']['item'][i]['local_batch_name'] == '本科一批' or info['data']['item'][i]['local_batch_name'] == '本科批':
                    temp = {'year': info['data']['item'][i]['year'],
                            'score': info['data']['item'][i]['average']}
                    wenA.append(temp)
                elif info['data']['item'][i]['local_batch_name'] == '本科二批':
                    temp = {'year': info['data']['item'][i]['year'],
                            'score': info['data']['item'][i]['average']}
                    wenB.append(temp)
                    break
            elif info['data']['item'][i]['local_type_name'] == '综合':
                temp = {'year': info['data']['item'][i]['year'],
                        'score': info['data']['item'][i]['average']}
                liA.append(temp)
                liB.append(temp)
                wenA.append(temp)
                wenB.append(temp)
                break
    # insert db
    # print(liA, liB, wenA, wenB)
    liAjson = {"type": "本科一批", "data": liA}
    liBjson = {"type": "本科二批", "data": liB}
    lijson = {"scoreLine": "理科", "data": [liAjson, liBjson]}
    wenAjson = {"type": "本科一批", "data": wenA}
    wenBjson = {"type": "本科二批", "data": wenB}
    wenjson = {"scoreLine": "文科", "data": [wenAjson, wenBjson]}
    c.execute(
        "INSERT INTO PROVINCELINE (NAME, TYPE, DATA) \
        VALUES ('%s', %d, '%s')" % (provinceName, 1, json.dumps(lijson)))
    c.execute(
        "INSERT INTO PROVINCELINE (NAME, TYPE, DATA) \
        VALUES ('%s', %d, '%s')" % (provinceName, 2, json.dumps(wenjson)))
    conn.commit()
    conn.close()
    result = ""
    if stype == "理科":
        result = lijson
    else:
        result = wenjson
    return result


def requestSchoolLine(schoolid, schoolName, provinceName, stype):
    '''
    request school score LINE.
    from 2017-2019.
    '''
    url = 'https://static-data.eol.cn/www/2.0/school/%d/info.json' % (schoolid)
    headers = headers = {'Accept': 'text/plain, application/json, */*',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.122 Safari/537.36'}
    result = requests.get(url, headers=headers)
    info = json.loads(result.text)
    if info['code'] != "0000":
        print('request school line Error')
        return ""
    provinceid = GprovinceID[provinceName]
    scoreLine = info['data']['pro_type_min'][str(provinceid)]
    li = []
    wen = []
    conn = sqlite3.connect('score.db')
    c = conn.cursor()
    for i in range(len(scoreLine)):
        if '1' in scoreLine[i]['type']:
            temp = {'year': scoreLine[i]['year']}
            temp['score'] = float(scoreLine[i]['type']['1'])
            li.append(temp)
        if '2' in scoreLine[i]['type']:
            temp = {'year': scoreLine[i]['year']}
            temp['score'] = float(scoreLine[i]['type']['2'])
            wen.append(temp)
        if '3' in scoreLine[i]['type']:
            temp = {'year': scoreLine[i]['year']}
            temp['score'] = float(scoreLine[i]['type']['3'])
            li.append(temp)
            wen.append(temp)
    lijson = {"type": "理科", "data": li}
    wenjson = {"type": "文科", "data": wen}
    c.execute(
        "INSERT INTO SCHOOLLINE (NAME, PROVINCE, TYPE, DATA) \
        VALUES ('%s', '%s', %d, '%s')" % (provinceName, provinceName, 1, json.dumps(lijson)))
    c.execute(
        "INSERT INTO SCHOOLLINE (NAME, PROVINCE, TYPE, DATA) \
        VALUES ('%s', '%s', %d, '%s')" % (provinceName, provinceName, 2, json.dumps(wenjson)))
    conn.commit()
    conn.close()
    if stype == "理科":
        return lijson
    else:
        return wenjson


def drawProvinceData(scoreList, provinceName, stype):
    '''
    draw province Score Line.\r\n
    only draw '本科'.\r\n
    only draw '文科' and '理科'.\r\n
    from 2014-2019.
    '''
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    for i in range(len(scoreList['data'][0]['data'])):
        x = scoreList['data'][0]['data'][i]['year']-2013
        y = scoreList['data'][0]['data'][i]['score']
        x1.append(x)
        y1.append(y)
    for i in range(len(scoreList['data'][1]['data'])):
        x = scoreList['data'][1]['data'][i]['year']-2013
        y = scoreList['data'][1]['data'][i]['score']
        x2.append(x)
        y2.append(y)

    group_labels = ['2014', '2015', '2016', '2017', '2018', '2019']
    plt.title('2014-2019年%s分数线(%s)' % (provinceName, stype))
    plt.xlabel('年度')
    plt.ylabel('分数')

    plt.plot(x1, y1, 'r', label='本科一批')
    plt.plot(x2, y2, 'b', label='本科二批')
    plt.xticks(x1, group_labels, rotation=0)
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.legend(bbox_to_anchor=[1, 1])
    plt.grid()
    plt.show()


def drawSchoolLine(provinceLine, schoolLine, schoolName, provinceName, stype):
    '''
    draw school/province Score Line.\r\n
    only draw '本科'.\r\n
    only draw '文科' and '理科'.\r\n
    '''
    x1 = []
    y1 = []
    x2 = []
    y2 = []
    x3 = []
    y3 = []
    for i in range(len(provinceLine['data'][0]['data'])):
        x = provinceLine['data'][0]['data'][i]['year']-2013
        y = provinceLine['data'][0]['data'][i]['score']
        x1.append(x)
        y1.append(y)
    for i in range(len(provinceLine['data'][1]['data'])):
        x = provinceLine['data'][1]['data'][i]['year']-2013
        y = provinceLine['data'][1]['data'][i]['score']
        x2.append(x)
        y2.append(y)
    for i in range(len(schoolLine['data'])):
        x = schoolLine['data'][i]['year']-2013
        y = schoolLine['data'][i]['score']
        x3.append(x)
        y3.append(y)

    group_labels = ['2014', '2015', '2016', '2017', '2018', '2019']
    plt.title('历年%s分数线(%s)-%s最低录取分数线' % (provinceName, stype, schoolName))
    plt.xlabel('年度')
    plt.ylabel('分数')

    plt.plot(x1, y1, 'r', label='本科一批')
    plt.plot(x2, y2, 'b', label='本科二批')
    plt.plot(x3, y3, 'g', label='%s最低录取分数线' % (schoolName))
    plt.xticks(x1, group_labels, rotation=0)
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.legend(bbox_to_anchor=[1, 1])
    plt.grid()
    plt.show()


def main():
    print('Demo of scoreLine')
    initDB()
    # handle school id
    schoolid = searchSchoolID(schoolName)
    if schoolid == -1:
        print('db search SCHOOLID not found')
        schoolid = requestSchoolID(schoolName)
        if schoolid == -1:
            print('SchoolName is NOT exist.')
            return
        else:
            insertSchoolID(schoolName, schoolid)
    else:
        print(schoolName, schoolid)

    # handle province score line
    if provinceName not in GprovinceID:
        print('provinceName is undefined.')
        return
    if typeName not in GtypeID:
        print('typeName is undefined')
        return
    provinceScoreLine = searchProvinceLine(provinceName, GtypeID[typeName])
    if provinceScoreLine == "":
        print('db search PROVINCE not found')
        provinceScoreLine = requestProvinceScoreLine(provinceName, typeName)
    print(provinceScoreLine)
    # drawProvinceData(provinceScoreLine, provinceName, typeName)

    # handle school line
    schoolLine = searchSchoolScoreLine(schoolName, provinceName, typeName)
    if schoolLine == "":
        print('db search SCHOOLLINE not found')
        schoolLine = requestSchoolLine(
            schoolid, schoolName, provinceName, typeName)
        if schoolLine == "":
            print('request Error')
            return
    print(schoolLine)
    drawSchoolLine(provinceScoreLine, schoolLine,
                   schoolName, provinceName, typeName)


if __name__ == '__main__':
    main()
