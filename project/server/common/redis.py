from flask import Flask
from redis import Redis


class FlaskRedis(object):

    def __init__(self, config: dict = None):
        self.redis = None
        if config:
            self.redis = Redis.from_url(config['REDIS_URL'])
        else:
            self.redis = Redis()

    def init_app(self, app: Flask):
        self.redis = Redis.from_url(app.config['REDIS_URL'])
