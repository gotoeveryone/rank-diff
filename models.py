# -*- coding: utf-8 -*-
"""
モデル
"""
class Rank(object):
    """
    段位モデル
    """
    def __init__(self, obj):
        self.rank_id = obj['rank_id']
        self.rank_name = obj['rank_name']
        self.count = obj['count']

    def __str__(self):
        return "{} dan is {}".format(self.rank_id, self.count)
