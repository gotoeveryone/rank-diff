"""
データベース関連
"""
import os
import pymysql
from models import Rank

class DatabaseConnect:
    """
    データベースへのアクセス情報
    """
    def __init__(self):
        self.name = os.environ.get("DB_NAME")
        self.user = os.environ.get("DB_USER")
        self.password = os.environ.get("DB_PASSWORD")

    def connect_db(self):
        """Open Connection to girlfriend"""

        __con = pymysql.connect(
            host='localhost',
            db=self.name,
            user=self.user,
            passwd=self.password,
            charset='utf8',
            cursorclass=pymysql.cursors.DictCursor)

        __cur = __con.cursor()
        return __con, __cur

class Dao:
    """
    データベースアクセスオブジェクト
    """
    def totalize(self, country_id: int):
        """
        集計処理
        """
        db_connect = DatabaseConnect()
        _, cur = db_connect.connect_db()

        query = "SELECT rank_id, ranks.name as rank_name, count(*) AS count\
            from players inner join ranks on players.rank_id = ranks.id \
            where country_id = %s group by rank_id order by rank_id desc"
        cur.execute(query, country_id)
        rows = cur.fetchall()
        return [Rank(row) for row in rows]
