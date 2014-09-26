"""
Implementation of the objects holding the operations executable on the database by handlers and modules.
Used for convenience and readability as well as adaptability for different database types.

This is currently the recommended method for accessing the database to ensure convenient overview of queries.
"""
import sys
from pathlib import Path

from core.database import escape, DatabaseError, InterfaceError, Database
from framework.config_tools import read_config


import hashlib
from includes import bootstrap
import os
import datetime

__author__ = 'justusadam'


class Operations:

    _config_name = 'config.json'

    db = Database()

    def __init__(self):
        self.charset = 'utf-8'
        self.cursor = self.db.cursor()

    def __del__(self):
        """
        Ensures queries are committed
        :return:
        """
        self.db.commit()

    _queries = {}

    _tables = {}

    @property
    def tables(self):
        t = self.config['tables']
        return {k: t[k] for k in self._tables}

    @property
    def queries(self):
        return self._queries[self.db.db_type.lower()]

    def execute(self, query_name, *format_args, **format_kwargs):
        query = self.queries[query_name].format(*format_args, **format_kwargs)
        try:
            self.cursor.execute(query)
        except (DatabaseError, InterfaceError) as error:
            raise DBOperationError(query, error)

    def create_table(self, table, columns):
        self.db.create_table(table, columns)

    def create_all_tables(self):
        for table in self.tables:
            self.create_table(table, self.tables[table])

    def drop_tables(self, *tables):
        self.db.drop_tables(*tables)

    def fill_tables(self):
        pass

    def drop_all_tables(self):
        for table in self._tables:
            try:
                self.drop_tables(table)
            except:
                print('Could not drop table ' + table)

    def init_tables(self, drop_tables=True):
        if drop_tables:
            self.drop_all_tables()
        self.create_all_tables()
        self.fill_tables()

    @property
    def config(self):
        # I am not sure this is the most efficient way of determining the config path, but it appears to be the only one
        path = str(Path(sys.modules[self.__class__.__module__].__file__).parent / self._config_name)
        return read_config(path)


class ContentHandlers(Operations):

    _queries = {
        'mysql' : {
            'add_new': 'replace into content_handlers (handler_module, handler_name, path_prefix) values ({handler_module}, {handler_name}, {path_prefix});',
            'get_by_prefix': 'select handler_module from content_handlers where path_prefix={path_prefix};'
        }
    }

    _tables = {'content_handlers'}

    def add_new(self, handler_name, handler_module, path_prefix):
        self.execute('add_new', handler_module=escape(handler_module), handler_name=escape(handler_name), path_prefix=escape(path_prefix))
        self.db.commit()

    def get_by_prefix(self, prefix):
        self.execute('get_by_prefix', path_prefix=escape(prefix))
        result = self.cursor.fetchone()
        if result is None:
            raise DBOperationError('get_by_prefix', 'No Result')
        return result[0]


class ModuleOperations(Operations):

    #TODO load this from file
    _queries = {
        'mysql': {
            'get_id': 'select id from modules where module_name={module_name};',
            'get_path': 'select module_path from modules where module_name={module_name};',
            'set_active': 'update modules set enabled=1 where module_name={module_name};',
            'add_module': 'insert into modules (module_name, module_path, module_role) values ({module_name},{module_path},{module_role});',
            'update_path': 'update modules set module_path={module_path} where module_name={module_name};',
            'ask_active': 'select enabled from modules where module_name={module_name};',
            'get_enabled': 'select module_name, module_path from modules where enabled=1;'
        }
    }

    _tables = {'modules'}

    def fill_tables(self):
        self.add_module('core', 'core', 'core')

    def get_id(self, module_name):
        self.execute('get_id', module_name=escape(module_name))
        return self.cursor.fetchone()[0]

    def create_multiple_tables(self, *tables):
        for table in tables:
            try:
                self.db.create_table(**table)
            except DatabaseError as error:
                print('Error in Database Module Operations (create_table)')
                print(error)

    def get_path(self, module):
        self.execute('get_path', module_name=escape(module))
        return self.cursor.fetchone()[0]

    def set_active(self, module):
        self.execute('set_active', module_name=escape(module))

    def add_module(self, module_name, module_path, module_role):
        self.execute('add_module', module_name=escape(module_name), module_path=escape(module_path), module_role=escape(module_role))

    def update_path(self, module_name, path):
        self.execute('update_path', module_path=escape(path), module_name=escape(module_name))

    def ask_active(self, module):
        self.execute('ask_active', module_name=escape(module))
        return self.cursor.fetchone()[0]

    def get_enabled(self):
        self.execute('get_enabled')
        acc = []
        for module in self.cursor.fetchall():
            acc.append({'name': module[0], 'path': module[1]})
        return acc


class Alias(Operations):

    _queries = {
        'mysql': {
            'by_alias': 'select source_url from alias where alias={alias};',
            'by_source': 'select alias from alias where source_url={source};',
            'add_alias': 'insert into alias (alias, source_url) values ({alias}, {source});'
        }
    }

    _tables = {'alias'}

    def get_by_alias(self, alias):
        self.execute('by_alias', alias=escape(alias))
        return self.cursor.fetchone()[0]

    def get_by_source(self, source):
        self.execute('by_source', source=escape(source))
        return [a[0] for a in self.cursor.fetchall()]

    def add_alias(self, source, alias):
        self.execute('add_alias', source=escape(source), alias=escape(alias))


class ContentTypes(Operations):

    _tables = {'content_types'}

    _queries = {
        'mysql': {
            'add': 'insert into content_types (content_type_name, display_name, content_handler, theme, description) values ({content_type_name}, {display_name}, {content_handler}, {theme}, {description});',
            'get_theme': 'select theme from content_types where content_type_name={content_type};',
            'get_content_types': 'select content_type_name, display_name from content_types;',
            'get_display_name': 'select display_name from content_types where content_type_name={content_type_name};'
        }
    }

    def add(self, content_type_name, display_name, content_handler, theme, description=''):
        self.execute('add', display_name=escape(display_name), content_type_name=escape(content_type_name), content_handler=escape(content_handler), theme=escape(theme), description=escape(description))

    def get_theme(self, content_type):
        self.execute('get_theme', content_type=escape(content_type))
        return self.cursor.fetchone()[0]

    def get_content_types(self):
        self.execute('get_content_types')
        return self.cursor.fetchall()

    def get_ct_display_name(self, ct_name):
        self.execute('get_display_name', content_type_name=escape(ct_name))
        return self.cursor.fetchone()[0]


class DBOperationError(Exception):
    def __init__(self, query, error):
        self.query = query
        self.err = error


# both in seconds
# SESSION_LENGTH > 0 is unlimited session length
SESSION_LENGTH = -1
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
            'get_user_id': 'select id from cms_users where username={username};',
            'get_acc_grp': 'select access_group from cms_users where {cond};',
            'get_username': 'select username from cms_users where id={user_id};',
            'get_date_joined': 'select date_created from cms_users where {cond};'
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
        pairing = {'username': username, 'access_group': access_group, 'user_first_name': first_name, 'user_middle_name': middle_name, 'user_last_name': last_name, 'date_created': datetime.datetime.utcnow()}
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

    def get_acc_grp(self, uname_or_id):
        self.execute('get_acc_grp', cond=self.comp_cond(uname_or_id))
        return self.cursor.fetchone()[0]

    def get_username(self, user_id):
        self.execute('get_username', user_id=escape(user_id))
        return self.cursor.fetchone()[0]

    def comp_cond(self, uname_or_id):
        assert isinstance(uname_or_id, int) or isinstance(uname_or_id, str)
        if isinstance(uname_or_id, int):
            return 'id=' + escape(str(uname_or_id))
        elif uname_or_id.isalpha():
            return 'id=' + escape(uname_or_id)
        else:
            return 'username=' + escape(uname_or_id)

    def get_date_joined(self, uname_or_id):
        self.execute('get_date_joined', cond=self.comp_cond(uname_or_id))
        return self.cursor.fetchone()[0]


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
            self.execute('add_session', user_id=escape(user_id), sess_token=escape(token), exp_date=escape(new_time()))
        return token

    def close_session(self, user_id):
        self.execute('remove_session', user_id=escape(user_id))
        self.db.commit()

    def get_token(self, user_id):
        self.execute('get_token', user_id=escape(user_id))
        result = self.cursor.fetchone()
        if not result:
            return None
        token, exp_date = result
        if check_exp_time(exp_date):
            return token
        self.close_session(user_id)
        return None

    def get_user(self, token):
        self.execute('get_user', sess_token=escape(token))
        result = self.cursor.fetchone()
        if result:
            user_id, exp_date = result
            if check_exp_time(exp_date):
                return int(user_id)
            self.close_session(user_id)
        return None

    def refresh(self, user_id):
        self.execute('refresh', exp_date=escape(new_time()), user_id=escape(user_id))