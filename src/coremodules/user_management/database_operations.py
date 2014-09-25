from core.database_operations import Operations, escape, DBOperationError
import hashlib
from includes import bootstrap
import os
import datetime

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
            'add_user_auth': 'insert into cms_user_auth (username, salt, password) values ({username}, {salt}, {password});',
            'change_password': 'update cms_user_auth set password={password}, salt={salt} where username={username};',
            'get_pass_and_salt': 'select password, salt from cms_user_auth where username={username};',
            'get_user_id': 'select id from cms_users where username={username};'
        }
    }

    _tables = {'cms_user_auth', 'cms_users'}

    @property
    def config(self):
        con = super().config
        con['tables']['cms_user_auth'] = [a.format(salt_size=str(bootstrap.SALT_LENGTH), pass_size=str(bootstrap.HASH_LENGTH)) for a in con['tables']['cms_user_auth']]
        return con

    def get_id(self, username):
        self.execute('get_user_id', username=escape(username))
        return self.cursor.fetchone()[0]

    def add_user(self, username, password, access_group=1, first_name='', middle_name='', last_name=''):
        pairing = {'username': username, 'access_group': access_group, 'user_first_name': first_name, 'user_middle_name': middle_name, 'user_last_name': last_name}
        self.db.insert('cms_users', pairing)
        self.add_user_auth(username, password)

    def add_user_auth(self, username, password):
        hashed, salt = hash_and_new_salt(password)
        self.execute('add_user_auth', username=escape(username), password=escape(hashed), salt=escape(salt))

    def update_password(self,  password, username):
        hashed, salt = hash_and_new_salt(password)
        self.execute('change_password', password=escape(hashed), username=escape(username), salt=escape(salt))

    def get_pass_salt(self, username):
        self.execute('get_pass_and_salt', username=escape((username)))
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
        'mysql': {
            'add_session': 'insert into session (user_id, sess_token, exp_date) values ({user_id}, {sess_token}, {exp_date});',
            'get_user': 'select user_id, exp_date from session where sess_token={sess_token};',
            'get_token': 'select sess_token, exp_date from session where user_id={user_id};',
            'refresh': 'update session set exp_date={exp_date} where user_id={user_id};',
            'remove_session': 'delete from session where user_id={user_id};'
        }

    }

    _tables = {'session'}

    @property
    def config(self):
        con = super().config
        con['tables']['session'] = [a.format(token_length=SESS_TOKEN_LENGTH) for a in con['tables']['session']]
        return con

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
        else:
            token = new_token()
            self.execute('add_session', user_id=escape(user_id), sess_token=escape(token), exp_date=escape(self.new_time()))
        return token

    def close_session(self, user_id):
        self.execute('remove_session', user_id=escape(user_id))

    def get_token(self, user_id):
        self.execute('get_token', user_id=escape(user_id))
        result = self.cursor.fetchone()
        if not result:
            return None
        token, exp_date = result
        if self.check_exp_time(exp_date):
            return token
        self.close_session(user_id)
        return None

    def get_user(self, token):
        self.execute('get_user', sess_token=escape(token))
        result = self.cursor.fetchone()
        if result:
            user_id, exp_date = result
            if self.check_exp_time(exp_date):
                return int(user_id)
            self.close_session(user_id)
        return None

    def check_exp_time(self, exp_date):

        # This line circumvents the check if SESSION_TIME is set to a negative number
        if SESSION_LENGTH < 0:
            return True
        return exp_date > datetime.datetime.utcnow()

    def refresh(self, user_id):
        self.execute('refresh', exp_date=escape(self.new_time()), user_id=escape(user_id))

    def new_time(self):
        return datetime.datetime.utcnow() + datetime.timedelta(seconds=SESSION_LENGTH)