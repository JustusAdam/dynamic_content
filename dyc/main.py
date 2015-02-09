from dyc.application import main

__author__ = 'Justus Adam'

if __name__ == '__main__':
    def init():
        from demo_app import tss
        tss.init_tables()
        tss.initialize()

    # get folder containing settings
    f = __file__.rsplit('/', 1)[0]

    main.main(f + '/custom_settings.yml', init, project_dir=f)