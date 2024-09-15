from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, username):
        self.id = id
        self.email = email
        self.username = username

    @staticmethod
    def get(user_id):
        # This is a placeholder. We'll implement user retrieval later.
        return None
