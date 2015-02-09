import binascii
import os

from dyc.backend import orm
from . import register, Handler
from dyc.util import html
from dyc.http import RequestMethods, response
from dyc.includes import settings


__author__ = 'Justus Adam'

TOKEN_SIZE = 16

_form_identifier_name = 'form_id'

_form_token_name = 'form_token'


@register()
class AntiCSRFMiddleware(Handler):
    def handle_controller(self, dc_obj, handler, args, kwargs):
        request = dc_obj.request
        if request.method is not RequestMethods.post:
            return None
        if not settings['anti_csrf']:
            return None
        if not handler.options.get('anti_csrf', True):
            return None
        if (
            _form_token_name in request.query
            and _form_identifier_name in request.query
            ):
            if _validate(
                request.query[_form_identifier_name][0],
                request.query[_form_token_name][0]
                ):
                return None
        return response.Response(code=403)


def _validate(fid, token):
    try:
        a = ARToken.get(
            form_id=fid,
            token=binascii.unhexlify(
                (token.encode()
                if not isinstance(token, bytes) else token)
                )
            )
        if a:
            a.delete_instance()
            return True
    except orm.DoesNotExist:
        return False


class ARToken(orm.BaseModel):
    form_id = orm.CharField()
    token = orm.BlobField()


def gen_token():
    return os.urandom(TOKEN_SIZE)


def new():
    fid = binascii.hexlify(gen_token()).decode()
    token = gen_token()
    ARToken.create(form_id=fid, token=token)
    return fid, binascii.hexlify(token).decode()


class SecureForm(html.FormElement):
    def render_content(self):
        return super().render_content() + str(self.render_token())

    @staticmethod
    def render_token():
        tid, token = new()
        return html.ContainerElement(
            html.Input(
                input_type='hidden',
                name=_form_token_name,
                value=token
                ),
            html.Input(
                input_type='hidden',
                name=_form_identifier_name,
                value=tid
                ),
            additional={'style': 'display:none;'}
            )
