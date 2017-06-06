# encode=utf-8
"""
棋士一覧を抽出し、データベースの値と比較します。
"""
import datetime
import os
import re
import urllib.request
from bs4 import BeautifulSoup
from db import Dao
from utils import LOGGER
import utils

PATTERN = re.compile('.*([0-9])dan.*')
PATTERN_TW = re.compile('.*dan0([0-9]).*')

MESSAGES = []

COUNTRIES = {
    1: '日本',
    2: '韓国',
    3: '中国',
    4: '台湾',
}

def notice_diff(country_id: int, sites: dict):
    """
    データベース側と比較し、差分があれば通知を行う。
    :param country_id int
    :param sites dict
    """
    # メッセージがすでにあれば空文字を挿入
    # 最終的に配列をjoinするので、改行を複数出すための対策
    if len(MESSAGES) > 0:
        MESSAGES.append('')

    MESSAGES.append('%s' % (COUNTRIES[country_id]))
    for data in Dao().totalize(country_id):
        site = sites[data.rank_id]
        if site != data.count:
            LOGGER.warning(
                '登録データと件数が異なります。%s (Web: %d - DB: %d)',
                data.rank_name, site, data.count
            )
            MESSAGES.append('　%s (Web: %d - DB: %d)' % (data.rank_name, site, data.count))

def taiwan_diff():
    """
    台湾棋院所属棋士の差分
    """
    LOGGER.info('台湾棋院所属棋士の件数を確認します。')

    url = 'http://taiwango.org.tw/chesser.asp'
    html = urllib.request.urlopen(url)
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
    notice_diff(4, sites)

def baduk_diff():
    """
    韓国棋院所属棋士の差分抽出
    """
    LOGGER.info('韓国棋院所属棋士の件数を確認します。')

    url = 'http://www.baduk.or.kr/info/player_list.asp'
    html = urllib.request.urlopen(url)
    dom = BeautifulSoup(html, "html.parser")

    # 親コンテンツ
    content = dom.select_one('#content')
    if content is None:
        exit('content is None')

    # 段位を抜き出す
    sites = dict()
    for rank in content.select('.facetop'):
        img = rank.find('img').get('src')
        rank_num = int(PATTERN.match(img).group(1))
        if rank_num == 0:
            continue

        # 段位と棋士の数を取得
        table = rank.find_next('table')
        count = len(table.find_all('td'))
        sites[rank_num] = count

    # 差分確認
    notice_diff(2, sites)

if __name__ == '__main__':
    """
    棋士一覧からデータを取得
    """
    try:
        START = datetime.datetime.now()
        taiwan_diff()
        baduk_diff()

        # メール送信
        utils.send_mail(START, os.environ.get('MAIL_TO_ADDRESS'),\
            '段位差異検出', '\n'.join(MESSAGES))
    except Exception as ex:
        raise ex
