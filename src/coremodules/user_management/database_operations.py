from core.database_operations import Operations, escape
import hashlib
from includes import bootstrap
import os

__author__ = 'justusadam'


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(bootstrap.HASHING_ALGORITHM, password, salt, bootstrap.HASHING_ROUNDS, bootstrap.HASH_LENGTH)


def check_ident(password, salt, comp_hash):
    hashed = hash_password(bytes(password), bytes(salt))
    return hashed == bytes(comp_hash)


class UserOperations(Operations):

    _queries = {
        'mysql': {
            'add_user': 'insert into cms_user_auth (user_name, salt, password) values ({user_name}, {salt}, {password});',
            'change_password': 'update cms_user_auth set password={password}, salt={salt} where user_name={user_name};',
            'get_pass_and_salt': 'select from cms_user_auth (password, salt) where user_name={user_name};'
        }
    }

    _tables = {'user_auth'}

    def config(self):
        con =  super().config
        con['tables'] = con['tables'].format(salt_size=str(bootstrap.SALT_LENGTH), pass_size=str(bootstrap.HASH_LENGTH))
        return con

    def add_user(self, username, password):
        salt = os.urandom(bootstrap.SALT_LENGTH)
        hashed = hash_password(bytes(password), bytes(salt))
        self.execute('add_user', user_name=escape(username), password=escape(hashed), salt=escape(salt))

    def update_password(self,  password, username):
        salt = os.urandom(bootstrap.SALT_LENGTH)
        hashed = hash_password(bytes(password), bytes(salt))
        self.execute('change_password', password=escape(hashed), user_name=escape(username), salt=escape(salt))

    def get_pass_salt(self, username):
        self.execute('get_pass_and_salt', user_name=escape((username)))
        return self.cursor.fetchone()

    def change_password(self, username, old_password, new_password):
        (pass_from_db, salt) = self.get_pass_salt(username)
        if check_ident(old_password, salt, pass_from_db):
            self.update_password(new_password, username)
        else:
            raise PermissionError