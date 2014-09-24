from core.database_operations import Operations, escape, DBOperationError
import hashlib
from includes import bootstrap
import os
import time

__author__ = 'justusadam'


#in seconds
SESSION_LENGTH = 300
SESS_TOKEN_LENGTH = 16


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(bootstrap.HASHING_ALGORITHM, password, salt, bootstrap.HASHING_ROUNDS, bootstrap.HASH_LENGTH)


def check_ident(password, salt, comp_hash):
    hashed = hash_password(password.encode(), salt)
    return hashed == bytes(comp_hash)


def hash_and_new_salt(password):
    salt = os.urandom(bootstrap.SALT_LENGTH)
    hashed = hash_password(password.encode(), salt)
    return hashed, salt


class UserOperations(Operations):

    _queries = {
        'mysql': {
            'add_user': 'insert into cms_user_auth (user_name, salt, password) values ({user_name}, {salt}, {password});',
            'change_password': 'update cms_user_auth set password={password}, salt={salt} where user_name={user_name};',
            'get_pass_and_salt': 'select password, salt from cms_user_auth where user_name={user_name};'
        }
    }

    _tables = {'cms_user_auth', 'cms_user'}

    @property
    def config(self):
        con = super().config
        con['tables']['cms_user_auth'] = [a.format(salt_size=str(bootstrap.SALT_LENGTH), pass_size=str(bootstrap.HASH_LENGTH)) for a in con['tables']['cms_user_auth']]
        return con

    def add_user_auth(self, username, password):
        hashed, salt = hash_and_new_salt(password)
        self.execute('add_user', user_name=escape(username), password=escape(hashed), salt=escape(salt))

    def update_password(self,  password, username):
        hashed, salt = hash_and_new_salt(password)
        self.execute('change_password', password=escape(hashed), user_name=escape(username), salt=escape(salt))

    def get_pass_salt(self, username):
        self.execute('get_pass_and_salt', user_name=escape((username)))
        return self.cursor.fetchone()

    def change_password(self, username, old_password, new_password):
        (pass_from_db, salt) = self.get_pass_salt(username)
        if check_ident(old_password, salt, pass_from_db):
            self.update_password(new_password, username)
        else:
            raise DBOperationError

    def authenticate_user(self, username, password):
        pass_from_db, salt = self.get_pass_salt(username)
        return check_ident(password, salt, pass_from_db)


def new_token():
    return os.urandom(SESS_TOKEN_LENGTH)


class SessionOperations(Operations):

    _queries = {
        'add_session': 'insert into session (user_id, sess_token, exp_date) values ({user_id}, {sess_token}, {exp_date});',
        'get_user': 'select user_id, exp_date from session where sess_token={sess_token};',
        'get_token': 'select token, exp_date from session where user_id={user_id};',
        'refresh': 'update session set exp_date={exp_date} where user_id={user_id};'
    }

    def check_session(self, token):
        user_id = self.get_user(token)
        if user_id:
            self.refresh(user_id)
            return user_id
        return None

    def add_session(self, user_id):
        token = self.get_token(user_id)
        if token:
            self.refresh(user_id)
            return token
        else:
            self.execute('add_session', user_id=escape(user_id), sess_token=escape(new_token()), exp_date=escape(self.new_time()))

    def get_token(self, user_id):
        self.execute('get_token', user_id=escape(user_id))
        result = self.cursor.fetchone()
        if not result:
            return None
        token, exp_date = result
        if self.check_exp_time(exp_date):
            return token
        return None

    def get_user(self, token):
        self.execute('get_user', sess_token=escape(token))
        result = self.cursor.fetchone()
        user_id, exp_date = result
        if result:
            if self.check_exp_time(exp_date):
                return user_id
        return None

    def check_exp_time(self, exp_date):

        # This line circumvents the check if SESSION_TIME is set to a negative number
        if SESSION_LENGTH < 0:
            return True
        return self.to_py_time(exp_date) > time.gmtime()

    def to_py_time(self, value):
        time.strptime(value, self.db.date_time_format)

    def to_db_time(self, value):
        time.strftime(self.db.date_time_format, value)

    def refresh(self, user_id):
        self.execute('refresh', exp_date=escape(self.new_time()), user_id=escape(user_id))

    def new_time(self):
        return self.to_db_time(time.gmtime(time.time() + SESSION_LENGTH))