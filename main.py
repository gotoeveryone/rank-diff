# -*- coding: utf-8 -*-
"""
棋士一覧を抽出し、データベースの値と比較します。
"""
import datetime
import os
from os.path import join, dirname
import re
import urllib2 as urllib
from bs4 import BeautifulSoup
from db import Dao
from dotenv import load_dotenv
import utils

# .envから環境変数を取得
DOTENV_PATH = join(dirname(__file__), '.env')
load_dotenv(DOTENV_PATH)

# ロガー
LOGGER = utils.get_logger()

PATTERN_KR_RANK = re.compile('.*([0-9])dan.*')
PATTERN_KR_COUNT = re.compile('.*\'([0-9]{1,2}).\'.*')
PATTERN_TW = re.compile('.*dan0([0-9]).*')

MESSAGES = [
    u'WEBと差分が発生しています。',
]

COUNTRIES = {
    1: u'日本',
    2: u'韓国',
    3: u'中国',
    4: u'台湾',
}

def notice_diff(country_id, sites):
    """
    データベース側と比較し、差分があれば通知を行う。
    :param country_id int
    :param sites dict
    """
    # メッセージがすでにあれば空文字を挿入
    # 最終的に配列をjoinするので、改行を複数出すための対策
    if MESSAGES:
        MESSAGES.append('')

    MESSAGES.append('%s' % (COUNTRIES[country_id]))
    has_diff = False
    for data in Dao().totalize(country_id):
        site = sites[data.rank_id]
        if site != data.count:
            LOGGER.warning(
                u'登録データと件数が異なります。%s (Web: %d - DB: %d)',
                data.rank_name, site, data.count
            )
            MESSAGES.append(u'　%s (Web: %d - DB: %d)' % (data.rank_name, site, data.count))
            if not has_diff:
                has_diff = True

    return has_diff

def taiwan_diff():
    """
    台湾棋院所属棋士の差分
    :return bool 差分があればTrue
    """
    LOGGER.info(u'台湾棋院所属棋士の件数を確認します。')

    url = 'http://taiwango.org.tw/chesser.asp'
    html = urllib.urlopen(url)
    dom = BeautifulSoup(html, "html.parser")

    # セレクタ指定が大変なのでwidth属性の指定で検索
    table = dom.select_one('table[width=685]')
    if table is None:
        exit('table is None')

    # 段位を抜き出す
    sites = dict()

    # 6行目から開始
    row_num = 5
    rows = table.select('tr')
    for idx, row in enumerate(rows):
        if idx != row_num:
            continue

        # 1行上は段位
        rank_img = rows[idx - 1].select_one('img')
        rank_num = int(PATTERN_TW.match(rank_img.get('src')).group(1))

        cell = row.select('td div')
        count = len(cell)

        sites[rank_num] = count

        # 次の対象は3行後なので飛ばす
        row_num += 3

    # 差分確認
    return notice_diff(4, sites)

def korean_diff():
    """
    韓国棋院所属棋士の差分抽出
    :return bool 差分があればTrue
    """
    LOGGER.info(u'韓国棋院所属棋士の件数を確認します。')

    url = 'http://www.baduk.or.kr/info/player_list.asp'
    html = urllib.urlopen(url)
    dom = BeautifulSoup(html, "html.parser")

    # 親コンテンツ
    content = dom.select_one('#content')
    if content is None:
        exit('content is None')

    # 段位を抜き出す
    sites = dict()
    for rank in content.select('.facetop'):
        img = rank.find('img').get('src')
        rank_num = int(PATTERN_KR_RANK.match(img).group(1))
        if rank_num == 0:
            continue

        # 段位と棋士の数を取得
        table = rank.find_next('table')
        player_sum = table.find_next('script').get_text()
        sites[rank_num] = int(PATTERN_KR_COUNT.match(player_sum).group(1))

    # 差分確認
    return notice_diff(2, sites)

if __name__ == '__main__':
    """
    棋士一覧からデータを取得
    """
    try:
        START = datetime.datetime.now()
        TAIWAN_DIFF = taiwan_diff()
        KOREAN_DIFF = korean_diff()

        # メール送信
        if (TAIWAN_DIFF or KOREAN_DIFF) and bool(int(os.environ.get('MAIL_SEND'))):
            utils.send_mail(START, os.environ.get('MAIL_TO_ADDRESS'),\
                u'段位差異検出', '\n'.join(MESSAGES))
    except Exception as ex:
        raise ex
