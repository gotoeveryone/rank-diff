# -*- coding: utf-8 -*-
"""
データベース関連
"""
import os
import pymysql
from models import Rank

class DatabaseConnect(object):
    """
    データベースへのアクセス情報
    """
    def __init__(self):
        self.host = os.environ.get("DB_HOST")
        self.name = os.environ.get("DB_NAME")
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASSWORD")

    def connect_db(self):
        """Open Connection to girlfriend"""

        __con = pymysql.connect(
            host=self.host,
            db=self.name,
            user=self.user,
            passwd=self.password,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor)

        __cur = __con.cursor()
        return __con, __cur

class Dao(object):
    """
    データベースアクセスオブジェクト
    """
    def totalize(self, country_id):
        """
        集計処理
        """
        db_connect = DatabaseConnect()
        _, cur = db_connect.connect_db()

        query = "SELECT rank_id, ranks.name as rank_name, count(*) AS count\
            from players inner join ranks on players.rank_id = ranks.id \
            where country_id = %s and is_retired = 0 group by rank_id order by rank_id desc"
        cur.execute(query, country_id)
        rows = cur.fetchall()
        return [Rank(row) for row in rows]
