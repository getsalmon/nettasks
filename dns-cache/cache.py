import time


class CacheRecord:
    def __init__(self, ans):
        self.ans = ans
        self.time = time.time()
        self.ttl = ans.ttl
