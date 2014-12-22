__author__ = 'justusadam'

from dynct.modules.form import tokens, model


def _print_db():
    print([tokens._form_identifier_name + ': ' + c.form_id + '; ' + tokens._form_token_name + ': ' + str(c.token) for c in model.ARToken.select()])