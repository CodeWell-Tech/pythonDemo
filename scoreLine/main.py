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

schoolName = '武汉大学'
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
                    liA.append(info['data']['item'][i]['average'])
                elif info['data']['item'][i]['local_batch_name'] == '本科二批':
                    liB.append(info['data']['item'][i]['average'])
            if info['data']['item'][i]['local_type_name'] == '文科':
                if info['data']['item'][i]['local_batch_name'] == '本科一批' or info['data']['item'][i]['local_batch_name'] == '本科批':
                    wenA.append(info['data']['item'][i]['average'])
                elif info['data']['item'][i]['local_batch_name'] == '本科二批':
                    wenB.append(info['data']['item'][i]['average'])
            # else:
            #     liA.append(info['data']['item'][i]['average'])
            #     liB.append(info['data']['item'][i]['average'])
            #     wenA.append(info['data']['item'][i]['average'])
            #     wenB.append(info['data']['item'][i]['average'])
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


def drawProvinceData(scoreList, provinceName, stype):
    '''
    draw province Score Line.\r\n
    only draw '本科'.\r\n
    only draw '文科' and '理科'.\r\n
    from 2014-2019.
    '''

    x1 = [1, 2, 3, 4, 5, 6]
    y1 = scoreList['data'][0]['data']

    x2 = [1, 2, 3, 4, 5, 6]
    y2 = scoreList['data'][1]['data']

    group_labels = ['2014', '2015', '2016', '2017', '2018', '2019']
    plt.title('2014-2019年%s分数线(%s)' % (provinceName, stype))
    plt.xlabel('年度')
    plt.ylabel('分数')

    plt.plot(x1, y1, 'r', label='本科一批')
    plt.plot(x2, y2, 'b', label='本科二批')
    plt.xticks(x1, group_labels, rotation=0)
    plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
    plt.legend(bbox_to_anchor=[0.3, 1])
    plt.grid()
    plt.show()


def main():
    print('Demo of scoreLine')
    initDB()
    # hanlde school id
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
    drawProvinceData(provinceScoreLine, provinceName, typeName)


if __name__ == '__main__':
    main()
