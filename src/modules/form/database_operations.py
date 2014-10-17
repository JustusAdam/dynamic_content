import os

from core.database_operations import Operations, escape


__author__ = 'justusadam'

TOKEN_SIZE = 16


def gen_token():
    return os.urandom(TOKEN_SIZE)


class FormOperations(Operations):
    _tables = {'form_tokens'}

    _queries = {
        'mysql': {
            'add_token': 'insert into form_tokens (url, token) values ({form}, {token});',
            'validate': 'select url from form_tokens where url={form} and token={token};',
            'remove': 'delete from form_tokens where url={form} and token={token};'
        }
    }

    def new_token(self, form):
        token = gen_token()
        self.execute('add_token', form=escape(form), token=escape(token))
        return token

    def validate(self, form, token):
        self.execute('validate', form=escape(form), token=escape(token))
        if self.cursor.fetchone():
            self.remove(form, token)
            return True
        return False

    def remove(self, form, token):
        assert isinstance(token, bytes)
        self.execute('remove', form=escape(form), token=escape(token))