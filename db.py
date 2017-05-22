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
    def totalize(country_id: int):
        db_connect = DatabaseConnect()
        con, cur = db_connect.connect_db()

        query = "SELECT rank_id, count(*) AS count FROM players \
             where country_id = %s group by rank_id order by rank_id desc"
        cur.execute(query, country_id)
        rows = cur.fetchall()
        return [Rank(row) for row in rows]
