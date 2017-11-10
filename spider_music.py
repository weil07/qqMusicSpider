import requests
import urllib
import json
from urllib import parse, request
import re
import xlwt
import sqlite3

headers = {
        'accept':'*/*',
        'accept-encoding':'gzip, deflate, br',
        'accept-language':'zh-CN, zh; q=0.8',
        'cookie':'pgv_pvi=322979840; RK=1gVii2yPEU; ptui_loginuin=1113629141; pgv_si=s2997176320; yq_index=0; qqmusic_fromtag=66; player_exist=1; yplayer_open=0; ptisp=ctc; ptcz=c5665ee7b483e4caf34a2bcb8672a5f82a9565e216c9cf03030256673b59d4b5; uin=o1113629141; skey=@H57m3H43w; pt2gguin=o1113629141; pgv_info=ssid=s1894420185; pgv_pvid=2083468240; ts_last=y.qq.com/portal/playlist.html; ts_uid=1761784800; ' \
                 'yqq_stat=0 dnt:1',
        'referer':'https://y.qq.com/portal/playlist.html',
        'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}
proxies = {'http': 'http://219.235.15.145:80'} ##添加代理ip，ip来自西刺http://www.xicidaili.com/
#获取歌单链接
def get_list_all(url=''):
    if not url:
        url = "https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?picmid=1&rnd=0.3612560456899254&g_tk=1891343775&jsonpCallback=getPlaylist&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&categoryId=10000000&sortId=5&sin=0&ein=29"
    html = requests.get(url,headers = headers, proxies=proxies).text

    #json解析处理
    getPlaylist = json.loads(html.strip('getPlaylist(').strip(')'))

    #获取信息
    song_list = []
    for list_item in getPlaylist['data']['list']:
        #拼接
        song_list_url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&disstid={0}&format=jsonp&g_tk=1891343775&jsonpCallback=playlistinfoCallback&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(list_item['dissid'])
        headers2 = {
                    'referer': 'https://y.qq.com/n/yqq/playlist/' + list_item['dissid'] + '.html',
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
                    }
        html_new = requests.get(song_list_url, headers=headers2, proxies=proxies).text
        song_list.append(html_new)
    #对下一页处理
    if getPlaylist['data']['ein'] < getPlaylist['data']['sum']:
        next_url = "https://c.y.qq.com/splcloud/fcgi-bin/fcg_get_diss_by_tag.fcg?picmid=1&rnd=0.3612560456899254&g_tk=1891343775&jsonpCallback=getPlaylist&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&categoryId=10000000&sortId=5&sin={0}&ein={1}".format(getPlaylist['data']['sin']+30,getPlaylist['data']['ein']+30)

    else:
        next_url = ''
    return next_url, song_list


#获取歌曲列表链接
def get_song_list(song_lists):
    one_song_list = []
    for html in song_lists:
        playlistinfoCallback = json.loads(html.strip('playlistinfoCallback(').strip(')'))
        print(playlistinfoCallback)
        for song in playlistinfoCallback['cdlist'][0]['songlist']:
            if 'songmid' in song.keys() and 'albummid' in song.keys():
                albumm_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg?albummid={0}&g_tk=5381&jsonpCallback=getAlbumInfoCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(
                    song['albummid'])
                onesong_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid={0}&tpl=yqq_song_detail&format=jsonp&callback=getOneSongInfoCallback&g_tk=5381&jsonpCallback=getOneSongInfoCallback&loginUin=0&hostUin=0&format=jsonp&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0'.format(
                    song['songmid'])
                refer = 'https://y.qq.com/n/yqq/song/' + song['songmid'] + '.html'
                one_song_list.append({'albummUrl': albumm_url, 'refer': refer, 'onesongUrl': onesong_url})
    return one_song_list

#获取单曲信息
def get_info_content(one_song_list):

    creat_sql()

    for one_song in one_song_list:
        songs = []
        headers['referer'] = one_song['refer']

        onesong_html = requests.get(one_song['onesongUrl'], headers=headers, proxies=proxies).text
        albumm_html = requests.get(one_song['albummUrl'], headers=headers, proxies=proxies).text
        # onesong_html = requests.get(one_song['onesongUrl']).text
        # albumm_html = requests.get(one_song['albummUrl']).text
        getOneSongInfoCallback = json.loads(onesong_html.strip('getOneSongInfoCallback(').strip(')'))
        getAlbumInfoCallback = json.loads(albumm_html.strip(' getAlbumInfoCallback(').strip(')'))
        song_dict = {}
        song_dict['media_mid']  = getOneSongInfoCallback['data'][0]['file']['media_mid']
        print("这是song_dict['media_mid']",song_dict['media_mid'])
        song_dict['songName'] = getOneSongInfoCallback['data'][0]['name']
        song_dict['singerName'] = getOneSongInfoCallback['data'][0]['singer'][0]['name']
        song_dict['time_public'] = getOneSongInfoCallback['data'][0]['album']['time_public']
        song_dict['genre'] = getAlbumInfoCallback['data']['genre']
        song_dict['lan'] = getAlbumInfoCallback['data']['lan']
        url_dict = getOneSongInfoCallback['url']
        for url_item in url_dict:
            song_dict['url'] = url_dict[url_item]
        print("这是url：", song_dict['url'])
        songs.append(song_dict)

        print("song_dict的类型是---", type(song_dict))
        print(song_dict)
        print("songs的类型是----", type(songs))
        print(songs)
        print("song_lists的类型：",song_lists)
        print((song_lists))

        download_music(song_dict)
        #save_excel(song_dict)
        save_sql(song_dict)

#以Excel存入
def save_excel(songs):
    fpath = '/Users/weil/Desktop/music/music_data/'
    book = xlwt.Workbook()
    sheet1 = book.add_sheet('sheet1', cell_overwrite_ok=False)
    sheet1.col(0).width = (20 * 256)
    sheet1.col(1).width = (20 * 256)
    sheet1.col(2).width = (20 * 256)
    sheet1.col(3).width = (20 * 256)
    sheet1.col(4).width = (20 * 256)
    sheet1.col(5).width = (20 * 256)
    sheet1.col(6).width = (60 * 256)

    # heads = ['media_mid', '歌名', '歌手', '发布时间', 'genre', 'lan', '链接']
    tempData = []
    # heads,values = [key for key,value in songs.items()]
    print()

    count = 0
    i = 1
    print('正在存入文件......')
    for key, value in songs.items():
        print('头是：', key)
        print('值是', value)
        sheet1.write(0, count, key)
        sheet1.write(i, count, value)
        count += 1
    i += 1
    # values = [value for value in songs.values()]
    # i = 1
    #
    # for value in values:
    #     print('值是', value)
    #     for j in range(len(values)):
    #         sheet1.write(i,j, value)
    #     i += 1
    book.save(fpath +'info' + '.xls')  # 括号里写存入的地址
    print('--- 存入Excel成功！---')

#创建数据库
def creat_sql():
    conn = sqlite3.connect('music_down.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS music '
                '(media_mid varchar(25), '
                '歌名 varchar(20), '
                '歌手 varchar(20), '
                '发布时间 varchar(20), '
                '类型 varchar(30), '
                'lan varchar(30), '
                '链接 varchar(100))')
    cur.close()
    conn.close()
    print("--- 建表成功！---")

#存入数据库
def save_sql(song_dict):

    conn = sqlite3.connect('music_down.db')
    cur = conn.cursor()
    #cur.execute('CREATE TABLE  music (media_mid varchar(20), 歌名 varchar(20), 歌手 varchar(20), 发布时间 varchar(20), genre varchar(20), lan varchar(20), 链接 varchar(60))')
    insert_sql = "INSERT INTO music (media_mid, 歌名, 歌手, 发布时间, 类型, lan, 链接) " \
                 "VALUES (\"{}\", \"{}\", \"{}\", \"{}\", \"{}\",\"{}\",\"{}\")".format(song_dict['media_mid'],
                                                                                        song_dict['songName'],
                                                                                        song_dict['singerName'],
                                                                                        song_dict['time_public'],
                                                                                        song_dict['genre'],
                                                                                        song_dict['lan'],
                                                                                        song_dict['url'])
    print(insert_sql)
    cur.execute(insert_sql)
    cur.close()
    conn.commit()
    conn.close()
    print("--- 存入数据库成功！---")

#下载单曲
def download_music(song_dict):
    #如下的代码完成了音乐文件的下载
    musicName = re.findall(r"/(.+?)\?", song_dict['url'])[0]
    url_adress = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?&jsonpCallback=MusicJsonCallback&cid=205361747&songmid=' + \
          song_dict['media_mid'] + '&filename=' + musicName + '&guid=6612300644'

    result_url = requests.get(url_adress)
    result_json = json.loads(result_url.text)
    print(result_url.text)
    print(result_json)
    vkey = result_json['data']['items'][0]['vkey']

    srcs =[]

    srcs.append('http://dl.stream.qqmusic.qq.com/'+musicName+'?vkey='+vkey+'&guid=6612300644&uin=0&fromtag=66')
    print(srcs)
    print('---歌曲 ['+song_dict['songName']+'] 开始下载！---')
    x = len(srcs)
    for m in range(0,x):
        print('---歌曲 '+song_dict['songName']+' - '+song_dict['singerName']+'.mp3 *****'+' 正在下载---')
        try:
            urllib.request.urlretrieve(srcs[m],'music_mp3/'+song_dict['songName']+' - '+song_dict['singerName']+'.mp3')
        except:
            x = x - 1
            print('Download wrong~')
    print('---歌曲 ['+song_dict['songName']+'] 下载完成！---')

#主函数
if __name__ == '__main__':
    song_lists = []
    next_url, song_lists = get_list_all()
    count = 1
    print('count=:', count)
    print("这是歌单：", song_lists)
    # song_lists.extend(song_lists)

    one_song_list = get_song_list(song_lists[:5])
    # 获取歌曲信信息列表
    get_info_content(one_song_list)
