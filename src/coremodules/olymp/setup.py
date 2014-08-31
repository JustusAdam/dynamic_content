from pymysql import DatabaseError
import pymysql

from . import database
from . import get_installed_core_modules

from src.tools.html_tools import html_element, input_element, form_element, table_element, list_element, stylesheet_link
from src.tools.config_tools import read_config
from coremodules.olymp.basic_page_handlers import PageHandler


__author__ = 'justusadam'


def try_database_connection():
    try:
        test_database = database.Database()
        if test_database.check_connection():
            return html_element(
                'The connection with the database was successfully established, you may continue with this setup',
                html_type='p') + html_element('Continue',
                                              html_type='a', classes=['continue', 'button'],
                                              additional_properties=['href="/setup/2"'])
        else:
            return html_element(
                'The connection with the database could not be established. Please review your settings and then reload this page',
                html_type='p')
    except DatabaseError:
        return html_element(
            'The connection with the database could not be established. Please review your settings and then reload this page',
            html_type='p')


class SetupHandler(PageHandler):
    def compile_page(self):
        config = read_config('config')
        setup_pages = {
            0: {
                'title': 'Setup of your CMS Installation',
                'content': html_element(
                    'The following steps will be taken during this setup',
                    html_type='h3'
                ) + list_element(
                    'Verifying Database Information',
                    'Configure site information',
                    'Set up an admin user',
                    list_type='ol'
                ) + html_element('Continue', html_type='a', classes=['continue', 'button'],
                                 additional_properties=['href="/setup/1"'])
            },
            1: {
                'title': 'Verifying Database Configuration',
                'content': table_element(
                    ['Type', config['database_type']],
                    ['Host', config['database_connection_arguments']['host']],
                    ['User', config['database_connection_arguments']['user']],
                    ['Password', config['database_connection_arguments']['passwd']],
                    ['Database Name', config['database_connection_arguments']['database']]
                ) + html_element(
                    'Please verify that these settings are correct or change them accordingly in the \'config.json\' file.',
                    html_type='p'
                ) + try_database_connection()
            },
            3: {
                'title': 'Create an admin account',
                'content': html_element(
                    'This page is a placeholder since the authorization is not yet implemented. Please click submit.'
                , classes='alert') +
                           form_element(
                               table_element(
                                   ['username:', input_element(name='username', end_line=False)],
                                   ['password:', input_element(input_type='password', name='password', end_line=False)],
                                   ['re-enter password:', input_element(input_type='password',
                                                                        name='confirm_password', end_line=False)],
                               ),
                               action='/setup/3?destination=/',
                               element_id='admin_form'
                           )
            },
            2: {
                'title': '{result}',
                'content': '{message}' + html_element('{link}', html_type='a',
                                                      classes=['continue', 'button'],
                                                      additional_properties=['href="{target}"'])
            }
        }
        generic = {
            'stylesheets': stylesheet_link('/theme/default_theme/css/style.css'),
            'scripts': '',
            'header': '',
            'footer': html_element('Python CMS 2014', element_id=''),
            'pagetitle': 'Setting up your CMS installation'
        }
        replacement_pattern = setup_pages[self.page_id]

        replacement_pattern.update(generic)

        setup_template = open('themes/default_theme/template/page.html')
        setup_template = setup_template.read()
        page = setup_template.format(**replacement_pattern)

        if self.page_id == 2:
            page = page.format(**self.setup_wrapper())
        self._document = page
        return 200

    def process_post(self, post_query):
        return self.page_id == 3

    def setup(self):
        from coremodules.olymp.database import Database
        from src.tools.config_tools import read_config

        db = Database()
        bootstrap = read_config('includes/bootstrap')

        if 'reset' in self.query:
            if self.query['reset'].lower() == 'true':
                try:
                    db.drop_tables(tuple(table['table_name'] for table in bootstrap['SETUP_TABLE_CREATION_QUERIES']))
                except DatabaseError as error:
                    print('printing error:')
                    print(error.args)
        try:
            for table in bootstrap['SETUP_TABLE_CREATION_QUERIES']:
                db.create_table(**table)
            for query in bootstrap['SETUP_DATABASE_POPULATION_QUERIES']:
                db.insert(**query)
            found_modules = get_installed_core_modules()
            for module in bootstrap['DEFAULT_MODULES']:
                try:
                    db.insert('modules', ('module_name', 'module_path'), (module, found_modules[module]))
                except pymysql.DatabaseError as error:
                    print(error)
            return True
        except pymysql.DatabaseError as err:
            print(err)
            return False

    def setup_wrapper(self):
        if self.setup():
            return {
                'result': 'Success',
                'message': html_element(
                    html_element('Your installation has been successful.', html_type='p') +
                    html_element('All necessary tables have been created and filled in the database',
                                 html_type='p') +
                    html_element('You may proceed.', html_type='p')
                ),
                'target': '/setup/3',
                'link': 'Continue'
            }
        else:
            return {
                'result': 'Failed',
                'message': html_element(
                    html_element('Your installation has failed.', html_type='p') +
                    html_element('Please revisit you settings and try again.', html_type='p') +
                    html_element('Please ensure the database does not contain any tables that this CMS'
                                 ' is trying to create', html_type='p') +
                    html_element('You may delete all existing tables that should be created by clicking reset',
                                 html_type='p')
                ) + html_element('Reset', html_type='a', classes='button',
                                 additional_properties=['href="/setup/2?reset=True"']),
                'target': '/setup',
                'link': 'Restart'
            }


def page_handler_factory(page_id, url_tail='', get_query=''):
    return SetupHandler(page_id, get_query)