import binascii
import os

from dyc.backend import orm
from dyc.util import html


__author__ = 'justusadam'

TOKEN_SIZE = 16

_form_identifier_name = 'form_id'

_form_token_name = 'form_token'


class ARToken(orm.BaseModel):
    form_id = orm.CharField()
    token = orm.BlobField()


def validation_hook(url):
    if 'form_token' in url.query:
        return validate(url.query)
    return True


def gen_token():
    return os.urandom(TOKEN_SIZE)


def _validate(fid, token):
    a = ARToken.get(form_id=fid, token=binascii.unhexlify(token))
    if a:
        a.delete_instance()
        return True
    else:
        return False


def validate(query):
    return _validate(fid=query[_form_identifier_name][0], token=query[_form_token_name][0])


def new():
    fid = binascii.hexlify(gen_token()).decode()
    token = gen_token()
    ARToken.create(form_id=fid, token=token)
    return fid, binascii.hexlify(token).decode()


class SecureForm(html.FormElement):
    def render_content(self):
        return super().render_content() + str(self.render_token())

    def render_token(self):
        tid, token = new()
        return html.ContainerElement(
            html.Input(input_type='hidden', name=_form_token_name, value=token),
            html.Input(input_type='hidden', name=_form_identifier_name, value=tid)
            , additional={'style': 'display:none;'})