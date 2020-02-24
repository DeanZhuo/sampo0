
from rhombus.models.core import *
from rhombus.models.ek import *
from rhombus.models.user import *

def search_user(dbsession, user):
    """get user id by name or id"""
    if type(user) == int:
        tuser = User.get(user)
    else:
        tuser = User.search(user, session=dbsession)

    return tuser
