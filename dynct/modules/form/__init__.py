from . import tokens


__author__ = 'justusadam'


def prepare():
    pass

def validation_hook(url):
    if 'form_token' in url.post:
        print(str(url.get_query))
        return tokens.validate(str(url), url.post['form_token'][0])
    return True