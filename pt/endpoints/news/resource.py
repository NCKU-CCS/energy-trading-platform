from flask import jsonify
from flask_restful import Resource

from utils.logging import logging
from utils.oauth import auth, g
from .model import News


class NewsResource(Resource):
    # pylint: disable=R0201
    @auth.login_required
    def get(self):
        logging.info(
            "[Get News Request]\nUser Account:%s\nUUID:%s\n" % (g.account, g.uuid)
        )
        news = [
            {
                "id": message.uuid,
                "time": message.publish_time.strftime("%Y/%m/%d %H:%M"),
                "content": message.content,
            }
            for message in News.query.order_by(News.time.desc()).limit(10).all()
        ]
        response = jsonify(news)
        return response

    # pylint: enable=R0201
