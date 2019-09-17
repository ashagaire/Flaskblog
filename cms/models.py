from cms import login_manager,mongo
from flask_login import UserMixin


@login_manager.user_loader
def load_user(username):
    u = mongo.db.users.find_one({'username': username})
    if not u:
        return None
    return User(u['_id'])


class User():
    
    
    def __init__(self, _id):
        self._id = _id
        

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id
    
        