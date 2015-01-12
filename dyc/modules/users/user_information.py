from dyc.core import mvc
from dyc import dchttp
from dyc.util import html
from dyc.modules import commons
from .login import LOGOUT_BUTTON
from . import users

__author__ = 'Justus Adam'


@commons.implements('user_information')
class UserInformationCommon(commons.Handler):
    source_table = 'user_management'

    def get_content(self, conf, render_args, client):
        return html.ContainerElement(
            html.ContainerElement(
                'Hello {}.'.format(' '.join([a for a in [
                    client.user.first_name,
                    client.user.middle_name,
                    client.user.last_name
                ] if a ])),
                html_type='p'),
            html.TableElement(
                ('Your Username: ', self.get_username(client.user)),
                ('Your Access Group: ', client.access_group.machine_name),
                ('You Joined: ', self.get_date_joined(client.user))
            ), LOGOUT_BUTTON
        )

    def title(self, conf):
        return 'User Information'

    def get_username(self, user):
        return users.get_user(user).username

    def get_date_joined(self, user):
        if user == users.GUEST:
            return 'Not joined yet.'
        return users.get_user(user).date_created


@mvc.controller_function('users/{int}', method=dchttp.RequestMethods.GET, query=False)
def user_information(model, uid):
    if not (
            ( model.client.check_permission('view other user info') or
            model.client.check_permission('view own user'))
            if int(uid) == model.client.user
            else model.client.check_permission('view other user info')
    ):
        return 'error'

    model['title'] = 'User Information'

    user = users.get_single_user(int(uid))
    grp = user.access_group
    model['content'] = html.ContainerElement(
        html.TableElement(
            ['UID', str(user.oid)],
            ['Username', user.username],
            ['Email-Address', user.email_address],
            ['Full name', ' '.join([user.user_first_name, user.user_middle_name, user.user_last_name])],
            ['Account created', user.date_created],
            ['Access Group', str(grp.oid) + ' (' + grp.machine_name + ')']
        )
    )
    return 'page'


@mvc.controller_function('users', method=dchttp.RequestMethods.GET, query=True)
def users_overview(model, get_query):
    if not model.client.check_permission('access users overview'):
        return 'error'
    model.theme = 'admin_theme'

    if 'selection' in get_query:
        selection = get_query['selection'][0]
    else:
        selection = '0,50'

    def all_users():
        for user in users.get_info(selection):
            yield [html.ContainerElement(str(user.oid), html_type='a', additional={'href': '/users/' + str(user.oid)}),
                   html.ContainerElement(user.username, html_type='a', additional={'href': '/users/' + str(user.oid)}),
                   ' '.join([user.user_first_name, user.user_middle_name, user.user_last_name]),
                   user.date_created,
                   html.ContainerElement('edit', html_type='a',
                                    additional={'href': '/users/' + str(user.oid) + '/edit'})]

    user_list = list(all_users())

    head = [['UID', 'Username', 'Name (if provided)', 'Date created', 'Actions']]

    model['title'] = 'User Overview'
    model['content'] = html.TableElement(*head + user_list, classes={'user-overview'}) if user_list else \
        html.ContainerElement(html.ContainerElement('It seems you do not have any users yet.',
                                          additional={'style': 'padding:10px;text-align:center;'}),
                         html.ContainerElement('Would you like to ', html.ContainerElement('create one', html_type='a',
                                                                                 additional={
                                                                                     'href': '/users/new',
                                                                                     'style': 'color:rgb(255, 199, 37);text-decoration:none;'}),
                                          '?', additional={'style': 'padding:10px;'}), additional={
                'style': 'padding:15px; text-align:center; background-color: cornflowerblue;color:white;border-radius:20px;font-size:20px;'})
