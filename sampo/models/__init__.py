
from rhombus.models.core import *
from rhombus.models.ek import *
from rhombus.models.user import *

def search_user(dbsession, user):
    """get user id by username or id"""
    if type(user) == int:
        tUser = User.get(user)
    else:
        tUser = User.search(user, session=dbsession)

    return tUser
