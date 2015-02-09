from dyc.util import html
from . import model, page


__author__ = 'Justus Adam'


ACCESS_DEFAULT_GRANTED = 0


def check_permission(access_type, client, name):
    if access_type == ACCESS_DEFAULT_GRANTED:
        return True
    return client.check_permission('access common ' + name)


class Handler(object):
    """Base handler for Commons"""
    type = 'type'

    @staticmethod
    def title(conf):
        return conf.machine_name

    def get_content(self, conf, render_args, client):
        raise NotImplementedError

    def compile(self, conf:model.CommonsConfig, render_args, show_title, client):
        if not check_permission(conf.access_type, client, conf.machine_name):
            return None

        title = html.ContainerElement(self.title(conf), html_type='h3') if show_title else ''
        obj = page.Component(
            html.ContainerElement(
                title,
                self.get_content(conf, render_args, client),
                classes={conf.machine_name.replace('_', '-'), 'common'}
            )
        )
        return obj
