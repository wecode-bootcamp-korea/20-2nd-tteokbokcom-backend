import re
from django.core.exceptions import ValidationError

class DuplicatedEntryError(Exception):
    def __init__(self, duplicated_field):
        super().__init__()
        self.err_message = f'Entry {duplicated_field} is duplicated.'

def validate_email(email):
    regex_email = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.]\w{2,3}$'

    if not re.search(regex_email, email):
        raise ValidationError(f"{email} is not an valid email.")

    return email

def validate_username(username):
    MIN_USERNAME_LENGTH = 2
    MAX_USERNAME_LENGTH = 40

    if len(username) < MIN_USERNAME_LENGTH or len(username) > MAX_USERNAME_LENGTH:
        raise ValidationError(f'Invalid Username, Use Useraname length between {MIN_USERNAME_LENGTH} and {MAX_USERNAME_LENGTH}')
        
    return username
    
def validate_password(password):
    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 20

    if len(password) < MIN_PASSWORD_LENGTH or len(password) > MAX_PASSWORD_LENGTH:
        raise ValidationError(f'Invalid Password Length, Use password length between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH}')

    return password

def validate_duplicate(model, data):
    non_duplicatable_fields = [
        field.attname
        for field in model._meta.get_fields()
        if not field.is_relation and field.unique
    ]

    for field in non_duplicatable_fields:

        if field in data.keys():
            field_to_check = {field: data[field]}
            
            if model.objects.filter(**field_to_check).exists():
                raise DuplicatedEntryError(field)