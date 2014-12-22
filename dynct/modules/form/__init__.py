from . import tokens


__author__ = 'justusadam'


def validation_hook(url):
    if 'form_token' in url.post:
        print(str(url.get_query))
        return tokens.validate(url.post)
    return True