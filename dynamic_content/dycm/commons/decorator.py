from dycm import theming
from framework.util import decorators, structures, html
from framework.machinery import component
from . import model, page


__author__ = 'Justus Adam'
__version__ = '0.2'


class Common:
    def __init__(self, name, content, item_type):
        self.name = name
        self.content = content
        self.item_type = item_type


# class RegionHandler:

def get_all_commons(client, name, theme):
    region_info = model.Common.select().where(
                    model.Common.region == name,
                    model.Common.theme == theming.model.Theme.get(
                        machine_name=theme
                        )
                    )
    if region_info:
        return [
            get_item(client, model.CommonsConfig.get(
                model.CommonsConfig.machine_name == a.machine_name),
                a.render_args, a.show_title)
            for a in region_info
            ]
    else:
        return []


@component.inject('CommonsMap')
def get_item(commons_map, client, item:model.CommonsConfig, render_args, show_title):

    content = commons_map[item.element_type].compile(
                item, render_args, show_title, client)

    return Common(item.machine_name, content, item.element_type)


def wrap(config, name, value):
    classes = ['region', 'region-' + name.replace('_', '-')]
    if 'classes' in config:
        if isinstance(config['classes'], str):
            classes.append(config['classes'])
        else:
            classes += config['classes']
    return html.ContainerElement(
        html.ContainerElement(
            *value,
            classes={'region-wrapper', 'wrapper'}
            ),
        classes=set(classes)
        )


def compile_region(region_name, region_config, theme, client):
    stylesheets = []
    meta = []
    scripts = []
    cont_acc = []
    commons = get_all_commons(client, region_name, theme)
    if commons:
        for item in commons:
            content = item.content
            if content:
                stylesheets += content.stylesheets
                meta += content.metatags
                scripts += content.metatags
                cont_acc.append(content.content)
        content = wrap(region_config, region_name, cont_acc)
    else:
        content = ''

    return page.Component(
        content,
        stylesheets=stylesheets,
        metatags=meta,
        scripts=scripts
        )


def add_regions(dc_obj):

    def _regions(client, theme):
        config = dc_obj.config['theme_config']['regions']
        return {
            region: compile_region(
                region,
                config[region],
                theme,
                client
                )
            for region in config
        }

    if 'regions' not in dc_obj.context:
        dc_obj.context['regions'] = _regions(
            dc_obj.request.client,
            dc_obj.config['theme']
            )

    return dc_obj


@decorators.apply_to_type(
    structures.DynamicContent,
    apply_before=False,
    return_from_decorator=False
    )
def Regions(dc_obj):
    theming.theme_dc_obj(dc_obj)
    add_regions(dc_obj)
