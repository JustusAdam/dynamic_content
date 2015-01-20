import datetime
import pathlib
from dyc.core import mvc
from dyc import dchttp


@mvc.controller_function('/upload', method=dchttp.RequestMethods.post, query=['file', 'name'])
def upload(model, file, name):
    file, name = file[0], name[0]
    name, ext = name.rsplit('.',1)

    if ext not in ['img', 'png', 'bmp']:
        return ':redirect:/upload/failed'

    dir = pathlib.Path('custom/files/public/images')

    filepath = dir / (name + str(datetime.datetime.now()) + '.' + ext)

    if not dir.exists():
        dir.mkdir()

    if filepath.exists():
        new = filepath.parent / (filepath.stem + '-1' + filepath.suffix)

    with open(str(filepath), mode='w') as fileobj:
        print(file, file=fileobj)

    return ':redirect:/upload'


@mvc.controller_function('/upload', method=dchttp.RequestMethods.get)
def upload_2(model):
    model['failed'] = False
    return 'fileupload'


@mvc.controller_function('/upload/failed', method=dchttp.RequestMethods.get)
def upload_failed(model):
    model['failed'] = True
    return 'fileupload'