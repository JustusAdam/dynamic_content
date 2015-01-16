"""
Implementation of the setup routine.

Currently uses the framework to dynamically create elements, once the basic site functionality has been implemented
and hardened this should be refactored to remove the framework elements and store the raw html in a separate file.
"""
from dyc.backend.database import Database
from dyc import dchttp, tss
from dyc.util import html
from dyc.core.mvc import decorator as mvc_dec
from dyc.includes import settings
from dyc.middleware import csrf
from dyc.modules.users import admin_actions as user_actions, users


__author__ = 'Justus Adam'
__version__ = '0.2'


def try_database_connection():
    try:
        test_database = Database()
        if test_database.check_connection():
            return html.ContainerElement(
                'The connection with the database was successfully established, you may continue with this setup',
                html_type='p') + html.ContainerElement('Continue', html_type='a', classes={'continue', 'button'},
                                                  additional={'href': '/setup/{next_page}'})
        else:
            return html.ContainerElement(
                'The connection with the database could not be established. Please review your settings '
                'and then reload this page', html_type='p')
    except IOError:
        return html.ContainerElement(
            'The connection with the database could not be established. Please review your settings and then '
            'reload this page', html_type='p')


def setup_pages(pid=0):
    if pid == 0:
        return {
            'title': 'Setup of your CMS Installation',
            'content': str(
                html.ContainerElement(
                    html.ContainerElement(
                        'Welcome to the setup process of your \'dynamic_content\' content management system.',
                        html_type='p'),
                    html.ContainerElement(
                        'These pages will guide you trough the necessary steps and tests that need to be taken to ensure \'dynamic_content\' will function properly for you.',
                        html_type='p'),
                    html.ContainerElement(
                        'During this process you will be required to enter and confirm sensible data to your installation as well as set a password for the administration user. It is therefore recommended that you perform this setup directly on the server or ahead of deployment or utilizing a secure and encrypted connection.',
                        html_type='p'),
                    html.ContainerElement(
                        'I hope that you will enjoy and be pleased with \'dynamic_content\'.', html_type='p'),
                    html.ContainerElement('Continue', html_type='a', classes={'continue', 'button'},
                                     additional={'href': '/setup/{next_page}'})
                )
            )
        }
    elif pid == 1:
        return {
                'title': 'Overview',
                'content': str(
                    html.ContainerElement(
                        html.ContainerElement('The following steps will be taken during this setup', html_type='h3'),
                        html.List(
                            'Verifying Database Information',
                            'Configure site information',
                            'Set up an admin user',
                            list_type='ul'
                        ),
                        html.ContainerElement('Continue', html_type='a', classes={'continue', 'button'},
                                         additional={'href': '/setup/{next_page}'})
                    )
                )
            }
    elif pid == 2:
        return {
            'title': 'Verifying Database Configuration',
            'content':
                str(
                    html.ContainerElement(
                        html.TableElement(
                            ['Type', settings.DATABASE.type],
                            ['Host', settings.DATABASE.host],
                            ['Database Name', settings.DATABASE.name],
                            ['User', settings.DATABASE.user],
                            ['Password', settings.DATABASE.password]),
                        html.ContainerElement('Please verify that these settings are correct or change '
                                         'them accordingly in the \'settings.py\' file.',
                                         html_type='p'),
                        '{db_con}'
                    )
                )
        }
    elif pid == 3:
        return {
            'title': 'Executing initial queries on the database',
            'content': str(
                html.ContainerElement(
                    html.ContainerElement(
                        'The following step will execute the initial queries to the database requred for \'dynamic_content\' to function. This will create new tables and fill them according to the installation specifications provided sufficient access to the database has been granted.',
                        html_type='p'),
                    html.ContainerElement('This step is required to proceed', html_type='p'),
                    html.ContainerElement(
                        'If you are certain, that the database has been properly configured to allow sufficient access to \'dynamic_content\' and are content with this software making changes to your database please click \'Continue\'',
                        html_type='p'),
                    html.ContainerElement('Continue', html_type='a', classes={'button', 'continue'},
                                     additional={'href': '/setup/{next_page}'})
                )
            )
        }
    elif pid == 4:
        return {
            'title': '{result}',
            'content': str(
                html.ContainerElement(
                    '{message}',
                    html.ContainerElement('{link}', html_type='a', classes={'continue', 'button'},
                                     additional={'href': '{target}'})))
        }
    elif pid == 5:
        return {
            'title': 'Create an admin account',
            'content': '{user_form}'
        }
    elif pid == 6: return {}



@mvc_dec.controller_function({'setup/{int}', 'setup'}, method=dchttp.RequestMethods.GET, query=False)
def setup_controller(model, pid):
    pid = int(pid)
    # config = read_config('cms/config')

    generic = {
        'sidebar_left': '<div class="sidebar" style="height: 1px;"></div>',
        'pagetitle': 'Setting up your CMS installation'
    }
    model.update(setup_pages(pid))

    model.update(generic)
    message = ''
    if pid == 2:
        db = Database
        model['content'] = model['content'].format(db_con=try_database_connection())
        del db
    if pid == 4:
        db = Database
        db.connect()
        setup_result = setup_wrapper()
        model['content'] = model['content'].format(**setup_result)
        model['title'] = model['title'].format(**setup_result)
        del db
    elif pid == 5:
        user_form = csrf.SecureForm(
            action='/setup/5'
        )
        model['content'] = model['content'].format(user_form=user_form)
    model['content'] = model['content'].format(this='/setup/' + str(pid),
                                                           next_page=pid + 1,
                                                           message=message)
    return 'page'


@mvc_dec.controller_function('setup/5', method=dchttp.RequestMethods.POST, query=True)
def create_initial_user(model, post):
    args = user_actions.post_to_args(post)
    try:
        users.add_user(**args)
        return ':redirect:/'
    except:
        return ':redirect:/setup/5'


def setup():
    from dyc import tss
    tss.init_tables()
    tss.initialize()


def setup_wrapper():
    if setup():
        return {
            'result': 'Success',
            'message': str(
                html.ContainerElement(
                    html.ContainerElement('Your installation has been successful.', html_type='p'),
                    html.ContainerElement('All necessary tables have been created and filled in the database',
                                     html_type='p'),
                    html.ContainerElement('You may proceed.', html_type='p'))),
            'target': '/setup/{next_page}',
            'link': 'Continue'
        }
    else:
        return {
            'result': 'Failed',
            'message': str(
                html.ContainerElement(
                    html.ContainerElement('Your installation has failed.', html_type='p'),
                    html.ContainerElement('Please revisit you settings and try again.',
                                     html_type='p'),
                    html.ContainerElement(
                        'Please ensure the database does not contain any tables that this CMS'
                        ' is trying to create', html_type='p'),
                    html.ContainerElement(
                        'You may delete all existing tables that should be created by clicking reset',
                        html_type='p'),
                    html.ContainerElement('Reset', html_type='a', classes={'button'},
                                     additional={'href': '{this}?reset=True'}))),
            'target': '/setup',
            'link': 'Restart'
        }
