# -*- coding: utf-8 -*-
from StringIO import StringIO
import glob
import os
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
import simplejson


def delete_file(fileField):
    "Elimina la imagen del campo para el modelo. Por ejemplo sobre Photo.img"
    if fileField.name:
        storage, path = fileField.storage, fileField.path
        storage.delete(path)


def tx_json_to_multipart(json_data):
    data_dic = simplejson.loads(json_data)
    for key, value in data_dic.iteritems():
        if len(value) > 10000:
            img_enc = data_dic[key].strip().decode('base64')
            # dec = base64.b64decode(data['img'])
            # fout = open('out.png', "w")
            # fout.write(dec)
            # fout.close()
            # and put in a dict with the rest of json data
            data_dic[key] = InMemoryUploadedFile(
                StringIO(img_enc),
                field_name='tempfile',
                name='tempfile.png',
                content_type='image/png',
                size=len(img_enc),
                charset='utf-8',
            )
            pass
    return data_dic


def delete_files(path):
    """
    Elimina todos los archivos dentro del path.
    ej: /path/to/media/delete_me*   ->  eliminará todos los archivos de /media
                                        que comienzen por delete_me
    """
    for filename in glob.glob(path):
        os.remove(filename)


def resize_img_width(img_path_from, img_path_to, fixed_width):
    """
    Redimensiona una imágen dado el ancho deseado para guardarla donde queramos
    """
    img = Image.open(img_path_from)
    if img.size[0] != fixed_width:
        wpercent = (fixed_width / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((fixed_width, hsize), Image.ANTIALIAS)
        img.save(img_path_to)


def resize_img_height(img_path, fixed_height):
    img = Image.open(img_path)
    if img.size[1] != fixed_height:
        hpercent = (fixed_height / float(img.size[1]))
        wsize = int((float(img.size[0]) * float(hpercent)))
        img = img.resize((wsize, fixed_height), Image.ANTIALIAS)
        img.save(img_path)