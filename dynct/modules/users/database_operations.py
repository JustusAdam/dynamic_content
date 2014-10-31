import hashlib
import os
import datetime

from dynct.core.database_operations import Operations, escape, DBOperationError
from dynct.includes import bootstrap


__author__ = 'justusadam'


# both in seconds
# SESSION_LENGTH > 0 is unlimited session length
SESSION_LENGTH = -1
SESS_TOKEN_LENGTH = 16


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(bootstrap.HASHING_ALGORITHM, password, salt, bootstrap.HASHING_ROUNDS,
                               bootstrap.HASH_LENGTH)


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
            'add_user_auth': 'insert into cms_user_auth (uid, salt, password) values ({uid}, {salt}, {password});',
            'change_password': 'update cms_user_auth set password={password}, salt={salt} where uid={uid};',
            'get_pass_and_salt': 'select password, salt from cms_user_auth where uid={uid};',
            'get_user_id': 'select uid from cms_users where username={username};',
            'get_acc_grp': 'select access_group from cms_users where {cond};',
            'get_username': 'select username from cms_users where uid={uid};',
            'get_date_joined': 'select date_created from cms_users where {cond};',
            'get_users': 'select uid, username, user_first_name, user_middle_name, user_last_name, date_created from cms_users order by uid limit {selection};',
            'get_single_user': 'select uid, username, email_address, user_first_name, user_middle_name, user_last_name, date_created from cms_users where {cond};'
        }
    }

    _tables = {'cms_users', 'cms_user_auth'}

    @property
    def config(self):
        con = super().config
        con['tables']['cms_user_auth'] = [
            a.format(salt_size=str(bootstrap.SALT_LENGTH), pass_size=str(bootstrap.HASH_LENGTH))
            for a in con['tables']['cms_user_auth']]
        return con

    def get_uid(self, username):
        self.execute('get_user_id', username=escape(username))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None

    def add_user(self, username, password, email, access_group=1, first_name='', middle_name='', last_name=''):
        pairing = {'username': username, 'access_group': access_group, 'user_first_name': first_name,
                   'email_address': email,
                   'user_middle_name': middle_name, 'user_last_name': last_name,
                   'date_created': datetime.datetime.utcnow()}
        self.db.insert('cms_users', pairing)
        self.add_user_auth(self.get_uid(username), password)
        self.db.commit()

    def add_user_auth(self, uid, password):
        hashed, salt = hash_and_new_salt(password)
        self.execute('add_user_auth', uid=escape(uid), password=escape(hashed), salt=escape(salt))

    def update_password(self, uid, password):
        hashed, salt = hash_and_new_salt(password)
        self.execute('change_password', password=escape(hashed), uid=escape(uid), salt=escape(salt))

    def get_pass_salt(self, uid):
        self.execute('get_pass_and_salt', uid=escape(uid))
        return self.cursor.fetchone()

    def change_password(self, uid, old_password, new_password):
        (pass_from_db, salt) = self.get_pass_salt(uid)
        if check_ident(old_password, salt, pass_from_db):
            self.update_password(uid, new_password)
        else:
            raise DBOperationError

    def authenticate_user(self, uid, password):
        result = self.get_pass_salt(uid)
        if not result:
            return False
        pass_from_db, salt = result
        return check_ident(password, salt, pass_from_db)

    def get_acc_grp(self, uname_or_uid):
        self.execute('get_acc_grp', cond=self.comp_cond(uname_or_uid))
        return self.cursor.fetchone()

    def get_username(self, uid):
        self.execute('get_username', uid=escape(uid))
        return self.cursor.fetchone()[0]

    def comp_cond(self, uname_or_uid):
        assert isinstance(uname_or_uid, int) or isinstance(uname_or_uid, str)
        if isinstance(uname_or_uid, int):
            return 'uid=' + escape(str(uname_or_uid))
        elif uname_or_uid.isalpha():
            return 'uid=' + escape(uname_or_uid)
        else:
            return 'username=' + escape(uname_or_uid)

    def get_date_joined(self, uname_or_uid):
        self.execute('get_date_joined', cond=self.comp_cond(uname_or_uid))
        return self.cursor.fetchone()[0]

    def get_users(self, selection='0,50'):
        self.execute('get_users', selection=selection)
        return self.cursor.fetchall()

    def edit_user(self, uid, **kwargs):
        self.db.update('cms_users', kwargs, where_condition='where uid=' + escape(uid))

    def get_single_user(self, uname_or_uid):
        cond = self.comp_cond(uname_or_uid)
        self.execute('get_single_user', cond=cond)
        return self.cursor.fetchone()


def new_token():
    return os.urandom(SESS_TOKEN_LENGTH)


def check_exp_time(exp_date):
    # This line circumvents the check if SESSION_TIME is set to a negative number
    if SESSION_LENGTH < 0:
        return True
    return exp_date > datetime.datetime.utcnow()


def new_time():
    return datetime.datetime.utcnow() + datetime.timedelta(seconds=SESSION_LENGTH)


class SessionOperations(Operations):
    _queries = {
        'mysql': {
            'add_session': 'insert into session (uid, sess_token, exp_date) values ({uid}, {sess_token}, {exp_date});',
            'get_user': 'select uid, exp_date from session where sess_token={sess_token};',
            'get_token': 'select sess_token, exp_date from session where uid={uid};',
            'refresh': 'update session set exp_date={exp_date} where uid={uid};',
            'remove_session': 'delete from session where uid={uid};'
        }

    }

    _tables = {'session'}

    @property
    def config(self):
        con = super().config
        con['tables']['session'] = [a.format(token_length=SESS_TOKEN_LENGTH) for a in con['tables']['session']]
        return con

    def check_session(self, token):
        uid = self.get_user(token)
        if uid:
            self.refresh(uid)
            return uid
        return None

    def add_session(self, uid):
        token = self.get_token(uid)
        if token:
            self.refresh(uid)
        else:
            token = new_token()
            self.execute('add_session', uid=escape(uid), sess_token=escape(token), exp_date=escape(new_time()))
            self.db.commit()
        return token

    def close_session(self, uid):
        self.execute('remove_session', uid=escape(uid))
        self.db.commit()

    def get_token(self, uid):
        self.execute('get_token', uid=escape(uid))
        result = self.cursor.fetchone()
        if not result:
            return None
        token, exp_date = result
        if check_exp_time(exp_date):
            return token
        self.close_session(uid)
        return None

    def get_user(self, token):
        self.execute('get_user', sess_token=escape(token))
        result = self.cursor.fetchone()
        if result:
            uid, exp_date = result
            if check_exp_time(exp_date):
                return int(uid)
            self.close_session(uid)
        return None

    def refresh(self, uid):
        self.execute('refresh', exp_date=escape(new_time()), uid=escape(uid))


class AccessOperations(Operations):
    _queries = {
        'mysql': {
            'check_permission': 'select permission from access_group_permissions where permission={permission} and (aid={aid}{default});',
            'remove_permission': 'delete from access_group_permissions where permission={permission} and aid={aid};',
            'remove_all_permissions': 'delete from access_group_permissions where permission={permission};'
        }
    }

    _tables = {'access_groups', 'access_group_permissions'}

    def check_permission(self, aid, default, permission):
        if default is not None:
            default = ' or aid=' + escape(default)
        else:
            default = ''
        self.execute('check_permission', permission=escape(permission), aid=escape(aid), default=default)
        return bool(self.cursor.fetchone())

    def add_permission(self, aid, permission):
        self.db.insert('access_group_permissions', {'permission': permission, 'aid': aid})
        self.db.commit()

    def add_group(self, aid, name):
        aid = int(aid)
        pairing = {'machine_name': name}
        if not aid < 0:
            pairing['aid'] = aid
        self.db.insert('access_groups', pairing)

    def remove_permission(self, aid, permission):
        self.execute('remove_permission', aid=escape(aid), permission=escape(permission))

    def remove_all_permissions(self, permission):
        self.execute('remove_all_permissions', permission=escape(permission))

    def get_access_group(self, aid=-1):
        assert isinstance(aid, int)
        condition = ';'
        if aid >= 0:
            condition = 'where aid=' + str(aid) + condition
        result = self.db.select(['aid', 'machine_name'], 'access_groups', condition)
        return result.fetchall()

    def get_permissions(self, aid=-1):
        assert isinstance(aid, int)
        condition = ';'
        if aid >= 0:
            condition = 'where aid=' + str(aid) + condition
        result = self.db.select(['aid', 'permission'], 'access_group_permissions', condition)
        return result.fetchall()