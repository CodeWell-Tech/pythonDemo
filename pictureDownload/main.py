import re
import requests
import progressbar


def dowmloadPic(html, keyword, bar):

    urlList = re.findall('"objURL":"(.*?)",', html, re.S)
    print('start downloading\r\n')

    for i, picURL in enumerate(urlList):
        try:
            pic = requests.get(picURL, timeout=10)
        except requests.exceptions.ConnectionError:
            print('当前图片无法下载')
            continue
        # suffix may be jpg, png
        suffix = picURL.split('.')[-1]
        filename = './picture/'+keyword+'_'+str(i) + '.' + suffix
        fp = open(filename, 'wb')
        fp.write(pic.content)
        fp.close()
        bar.update(int(((i+1) / 60) * 100))


# 1. 百度的原因，一次只返回60个图片。如果要求更多图片，控制pn参数即可。
# 2. quality参数，3=大尺寸，2=中尺寸，1=小尺寸。
if __name__ == '__main__':
    word = '杨超越'
    quality = 3
    bar = progressbar.ProgressBar().start()
    url = 'http://image.baidu.com/search/flip?tn=baiduimage&pn=0&word=%s&z=%d' % (
        word, quality)
    result = requests.get(url)
    dowmloadPic(result.text, word, bar)
    bar.finish()
    print('download finished.')
