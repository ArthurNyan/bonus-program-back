from flask_jwt_extended import create_access_token
from datetime import timedelta

class TokenFactory:
    @staticmethod
    def create_token(user_id):
        return create_access_token(identity=user_id, expires_delta=timedelta(hours=1))
