from rest_framework.authtoken.models import Token

'''
    Common Methods that are used by the entire backend
'''
from rest_framework.authtoken.models import Token


def get_token_by_user(user=None):
    return Token.objects.get(user=user)


def get_token_by_key(key=None):
    return Token.objects.get(key=key)



'''
    Assumes that user has already been validated
'''
def create_token(user=None):
    return Token.objects.create(user=user)


def create_token_user_id(user_id=None):
    return Token.objects.create(user_id=user_id)