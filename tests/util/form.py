__author__ = 'justusadam'

from dynct.modules import form


def _print_db():
    print([form._form_identifier_name + ': ' + c.form_id + '; ' + form._form_token_name + ': ' + str(c.token) for c in form.ARToken.select()])