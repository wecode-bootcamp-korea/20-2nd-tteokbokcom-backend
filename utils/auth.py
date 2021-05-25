import jwt
import time
import bcrypt

from tteokbok.settings import JWT_SECRET_KEY, JWT_ALGORITHM, JWT_DURATION_SEC

class UnauthorizationError(Exception):
    def __init__(self, err_msg = None):
        super().__init__()
        self.err_message = err_msg

def check_password(password, user):
    if not bcrypt.checkpw(password.encode('utf-8'),user.password.encode('utf-8')):
        raise UnauthorizationError("Wrong Password Entered.")
    
    return password

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def issue_token(user):
    new_token = jwt.encode(
                            {
                                'user_id': user.id,
                                'iat'    : int(time.time()),
                                'exp'    : int(time.time()) + JWT_DURATION_SEC
                            }, 
                            JWT_SECRET_KEY, 
                            JWT_ALGORITHM
                            )
    return new_token