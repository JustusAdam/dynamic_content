import binascii
import os
import peewee

from dyc.backend import orm
from dyc.core import middleware
from dyc.util import html
from dyc.dchttp import RequestMethods, response
from dyc.includes import settings


__author__ = 'justusadam'

TOKEN_SIZE = 16

_form_identifier_name = 'form_id'

_form_token_name = 'form_token'


@middleware.register()
class AntiCSRFMiddleware(middleware.Handler):
    def handle_view(self, request, handler, args, kwargs):
        if request.method is not RequestMethods.post:
            return None
        if not settings.ANTI_CSRF:
            return None
        if not handler.options.get('anti_csrf', True):
            return None
        if _form_token_name in request.query and _form_identifier_name in request.query:
            try:
                a = ARToken.get(
                    form_id=request.query[_form_identifier_name][0],
                    token=binascii.unhexlify(request.query[_form_token_name][0])
                    )
                if a:
                    a.delete_instance()
                    return None
            except peewee.DoesNotExist:
                pass
        return response.Response(code=403)



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

    def render_token(self):
        tid, token = new()
        return html.ContainerElement(
            html.Input(input_type='hidden', name=_form_token_name, value=token),
            html.Input(input_type='hidden', name=_form_identifier_name, value=tid)
            , additional={'style': 'display:none;'})