from dycc.application import main

__author__ = 'Justus Adam'

if __name__ == '__main__':
    def init():
        from testapp import tss
        tss.init_tables()
        tss.initialize()
    main.main('custom_settings.yml', init)