import datetime
import pathlib
from dycc import mvc
from dycc import http


@mvc.controller_function('/upload', method=http.RequestMethods.post, query=['file', 'name'])
def upload(dc_obj, file, name):
    file, name = file[0], name[0]
    name, ext = name.rsplit('.',1)

    if ext not in ['img', 'png', 'bmp']:
        return ':redirect:/upload/failed'

    target_dir = pathlib.Path('custom/files/public/images')

    filepath = target_dir / (name + str(datetime.datetime.now()) + '.' + ext)

    if not target_dir.exists():
        target_dir.mkdir()

    if filepath.exists():
        new = filepath.parent / (filepath.stem + '-1' + filepath.suffix)

    with open(str(filepath), mode='w') as fileobj:
        print(file, file=fileobj)

    return ':redirect:/upload'


@mvc.controller_function('/upload', method=http.RequestMethods.get)
def upload_2(dc_obj):
    dc_obj['failed'] = False
    return 'fileupload'


@mvc.controller_function('/upload/failed', method=http.RequestMethods.get)
def upload_failed(dc_obj):
    dc_obj['failed'] = True
    return 'fileupload'
