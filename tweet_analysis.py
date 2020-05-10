from requests_oauthlib import OAuth1Session
import json
from datetime import datetime
import calendar
import csv
import time
from bs4 import BeautifulSoup

# Twitter APIにアクセスするためのコード
consumer_key = '*****'
consumer_key_secret = '*****'
access_token = '*****'
access_token_secret = '*****'


# Twitter APIにアクセス
twitter = OAuth1Session(consumer_key, consumer_key_secret, access_token, access_token_secret)

# Twitterで検索するための関数を定義する。queは検索ワード、botはbotを含めるか否か、countは取得Tweet数、max_idは検索するTweetのIDの最大値。

def get(que,max_id):
    params = {'q': que, 'count': 100, 'max_id': max_id, 'modules': 'status', 'lang': 'ja'}
    # Twitterへアクセス。
    req = twitter.get("https://api.twitter.com/1.1/search/tweets.json", params=params)

    # アクセスに成功した場合、ツイート情報を保持する。
    if req.status_code == 200:
        search_timeline = json.loads(req.text)
        limit = req.headers['x-rate-limit-remaining']
        reset = int(req.headers['x-rate-limit-reset'])
        print("API remain: " + limit)
        if int(limit) == 1:
            print('sleep')
            time.sleep((datetime.fromtimestamp(reset) - datetime.now()).seconds)

    # 失敗した場合、プロセスを終了する。
    elif req.status_code == 503:
        time.sleep(30)
        req = twitter.get("https://api.twitter.com/1.1/search/tweets.json", params=params)
        if req.status_code == 200:
            search_timeline = json.loads(req.text)
            # API残り
            limit = req.headers['x-rate-limit-remaining']
            reset = int(req.headers['x-rate-limit-reset'])
            print("API remain: " + limit)
            if limit == 0:
                print('sleep')
                time.sleep((datetime.fromtimestamp(reset) - datetime.now()).seconds)

        else:
            print(req.status_code)
            return [], 0
    else:
        print(req.status_code)
        return [], 0

    for i in range(len(search_timeline['statuses'])):
        bs3obj = BeautifulSoup(search_timeline['statuses'][i]['source'], 'html.parser')
        search_timeline['statuses'][i]['source'] = bs3obj.text


    # この関数を実行した場合に、Tweet情報のリストを返す。
    return search_timeline['statuses'], search_timeline['statuses'][-1]['id']


def TweetSearch(que, bot, rep):
    max_id = 1259158522710730000 - 1
    global search_timeline, tweetTime
    tweetList = []
    # botによるツイートを除外するか否かを指定する。
    if bot:
        que = str(que + ' -bot -rt')
    else:
        que = str(que + ' -rt')

    for i in range(rep):
        time.sleep(1)
        result, max_id = get(que,max_id)
        if max_id == 0:
            break

        tweetList.extend(result)


    return tweetList



word = '#検察庁法改正案に抗議します'
tweetList = TweetSearch(word,False,200)

head = [i for i in tweetList[0]]

# CSVファイルに出力する
with open('tweetanalysis_02.csv','w',newline='', encoding='utf_8') as f:
    writter = csv.writer(f)
    writter.writerow(head)
    for i in tweetList:
        writter.writerow([i[key] for key in head])