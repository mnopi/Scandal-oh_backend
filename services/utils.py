# -*- coding: utf-8 -*-
from StringIO import StringIO
import glob
import logging
import os
from PIL import Image
from boto.s3.connection import S3Connection
from django.core.files.uploadedfile import InMemoryUploadedFile
import simplejson
import boto
from boto.s3.key import Key
from settings.common import *


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


class ImgResizer(object):
    """
    Redimensionador de imagen. Se construye con un ancho y/o alto dados.

    Ejemplos de uso:
        ImgResizer().resize('/path/to/img_from.png', '/path/to/img_to.png')
        ImgResizer().resize('/path/to/img_from.png', '/path/to/img_to.png', fixed_width=1024)
    """
    def __resize_width__(self):
        """Redimensiona al ancho deseado"""
        if self.img_width != self.fixed_width:
            wpercent = (self.fixed_width / float(self.img_width))
            hsize = int((float(self.img_height) * float(wpercent)))
            self.new_img = self.img.resize((self.fixed_width, hsize), Image.ANTIALIAS)

    def __resize_height__(self):
        """Redimensiona al alto deseado"""
        if self.img_height != self.fixed_height:
            hpercent = (self.fixed_height / float(self.img_height))
            wsize = int((float(self.img_width) * float(hpercent)))
            self.new_img = self.img.resize((wsize, self.fixed_height), Image.ANTIALIAS)

    def resize(self, img_from, img_to=None, **kwargs):
        self.fixed_width = kwargs['fixed_width'] if 'fixed_width' in kwargs else 480
        self.fixed_height = kwargs['fixed_height'] if 'fixed_height' in kwargs else 640
        self.img_from = img_from
        # si no se da una imagen destino se sobreescribe la origen
        self.img_to = img_to if img_to is not None else self.img_from
        self.img = Image.open(img_from)
        self.img_width = self.img.size[0]
        self.img_height = self.img.size[1]

        if self.img_width >= self.img_height:
            self.__resize_width__()
        else:
            self.__resize_height__()

        self.new_img.save(self.img_to)


class S3BucketHandler(object):

    def __init__(self):
        # set boto lib debug to critical
        logging.getLogger('boto').setLevel(logging.CRITICAL)
        # connect to the bucket
        conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        self.bucket = conn.get_bucket(BUCKET_NAME)

    def push_file(self, fn, file_id):
        """
        fn: archivo a subir, e.g. /var/www/data/paquillo.png
        file_id: para identificar el archivo dentro del bucket
        """
        # create a key to keep track of our file in the storage
        k = Key(self.bucket)
        k.key = file_id
        k.set_contents_from_filename(fn)
        # we need to make it public so it can be accessed publicly
        # using a URL like http://s3.amazonaws.com/bucket_name/key
        # http://scandaloh.s3.amazonaws.com/prueba.png
        k.make_public()
        # remove the file from the web server
        os.remove(fn)

    def remove_file(self, file_id):
        "Quita archivo del bucket"
        k = Key(self.bucket)
        k.key = file_id
        self.bucket.delete_key(k)

    def make_backup(self):
        """
        Hace copia de seguridad en LOCAL_PATH de todos los archivos
        alojados en el bucket
        """
        bucket_list = self.bucket.list()
        for l in bucket_list:
            keyString = str(l.key)
            # check if file exists locally, if not: download it
            if not os.path.exists(LOCAL_PATH + keyString):
                l.get_contents_to_filename(LOCAL_PATH + keyString)

