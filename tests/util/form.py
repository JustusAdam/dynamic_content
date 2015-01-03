__author__ = 'justusadam'

from dyc.modules import anti_csrf


def _print_db():
    print([anti_csrf._form_identifier_name + ': ' + c.form_id + '; ' + anti_csrf._form_token_name + ': ' + str(c.token) for c in anti_csrf.ARToken.select()])