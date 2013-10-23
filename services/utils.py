# -*- coding: utf-8 -*-
from StringIO import StringIO
import json
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