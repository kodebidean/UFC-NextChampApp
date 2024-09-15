from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, email, username, role='user'):
        self.id = id
        self.email = email
        self.username = username
        self.role = role

    @staticmethod
    def get(user_id):
        # This is a placeholder. We'll implement user retrieval later.
        return None

    def is_admin(self):
        return self.role == 'admin'
