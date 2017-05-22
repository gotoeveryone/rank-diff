"""
棋士一覧を抽出し、データベースの値と比較します。
"""
import urllib.request
import re
from bs4 import BeautifulSoup
from db import Dao

PATTERN = re.compile('.*([0-9])dan.*')

def baduk_diff():
    """
    韓国棋院所属棋士の差分抽出
    """
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

    # データベース側
    for data in Dao().totalize(2):
        site = sites[data.rank_id]
        if site != data.count:
            print("登録データと異なります。 %d - %d" % (site, data.count))

if __name__ == '__main__':
    """
    棋士一覧からデータを取得
    """
    try:
        baduk_diff()
    except Exception as ex:
        raise ex
