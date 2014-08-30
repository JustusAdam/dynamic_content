__author__ = 'justusadam'


def read_config(path, file_type='json'):
    import json
    with open(path + '.' + file_type, mode='r') as file:
        return json.load(file)


def write_config(config, path, file_type='json'):
    import json
    with open(path + '.' + file_type, mode='w') as file:
        json.dump(config, file, indent=4)
