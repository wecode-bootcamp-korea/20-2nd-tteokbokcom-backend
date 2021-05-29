import jwt

from users.models       import User
from tteokbok.settings  import JWT_SECRET_KEY, JWT_ALGORITHM

def decode_jwt(token):
    return jwt.decode(token, JWT_SECRET_KEY, JWT_ALGORITHM)
    
def get_user_from_jwt(token):
    payload = decode_jwt(token)
    user    = User.objects.get(pk=payload.get('user_id'))
    return user