# -*- coding: utf-8 -*-
from StringIO import StringIO
import glob
import logging
import os
import re
import subprocess
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from pydub import AudioSegment
import simplejson
import boto
from boto.s3.key import Key
from settings import common
from tests.utils import TEST_IMGS_COPIES_PATH


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
            data_dic[key] = InMemoryUploadedFile(
                StringIO(img_enc),
                field_name='tempfile',
                name='tempfile.png',
                content_type='image/png',
                size=len(img_enc),
                charset='utf-8',
            )
    return data_dic


def delete_files(path, exclude=None):
    """
    Elimina todos los archivos dentro del path.
    ej: /path/to/media/delete_me*   ->  eliminará todos los archivos de /media
                                        que comienzen por delete_me
    """
    for filename in glob.glob(path):
        if exclude and not exclude in filename:
            os.remove(filename)
        else:
            os.remove(filename)



class ImgHelper(object):
    COMPRESSOR = 'JPEG'
    COMPRESSION_QUALITY = 80
    DEFAULT_RESIZED_WIDTH = 480
    DEFAULT_RESIZED_HEIGHT = 640

    def __resize_width__(self):
        "Redimensiona al ancho deseado"
        if self.img_width != self.fixed_width:
            wpercent = (self.fixed_width / float(self.img_width))
            hsize = int((float(self.img_height) * float(wpercent)))
            self.img_resized = self.img.resize((self.fixed_width, hsize), Image.ANTIALIAS)

    def __resize_height__(self):
        "Redimensiona al alto deseado"
        if self.img_height != self.fixed_height:
            hpercent = (self.fixed_height / float(self.img_height))
            wsize = int((float(self.img_width) * float(hpercent)))
            self.img_resized = self.img.resize((wsize, self.fixed_height), Image.ANTIALIAS)

    def __compress__(self):
        "Comprime la imagen dada en formato jpg, sobreescribiendo la original"
        img = Image.open(self.img_from_path)
        self.img_compressed_path = self.__rename_to_jpg__(self.img_from_path)
        img.save(self.img_compressed_path, self.COMPRESSOR, quality=self.COMPRESSION_QUALITY)

    def __get_filename__(self, path):
        return re.sub(r'^.*\/(.*\..*)$', r'\1', path)

    def __rename_to_jpg__(self, path):
        """
        En modo test: devuelve renombrado a la carpeta para los tests
        Sin modo test: renombrado a la misma ruta origen
        """
        if common.UNIT_TEST_MODE:
            filename = re.sub(r'^.*\/(.*\.).*$', r'\1jpg', path)
            return os.path.join(TEST_IMGS_COPIES_PATH, filename)
        else:
            if not self.__is_jpg__(path):
                return re.sub(r'^(.*\.).*$', r'\1jpg', path)
            return path

    def __rename_to_p_jpg__(self, path):
        if common.UNIT_TEST_MODE:
            filename = re.sub(r'^.*\/(.*)\..*$', r'\1.p.jpg', path)
            return os.path.join(TEST_IMGS_COPIES_PATH, filename)
        else:
            return re.sub(r'^(.*)\..*$', r'\1.p.jpg', path)

    def __is_jpg__(self, path):
        return re.sub(r'^.*\.(.*)$', r'\1', path) == 'jpg'

    def resize(self, img_from, **kwargs):
        """
        Redimensionador de imagen. Se construye con un ancho y/o alto dados.

        **kwargs:
            fixed_width/heigh: redimensiona en píxeles a ancho/alto dado, e.g. fixed_width=1024

        Ejemplos:
            ImgResizer().resize('/path/to/img_from.png')

            En este caso se guardará en un .p.png, con un ancho dado de 1024px
                ImgResizer().resize('/path/to/img_from.png', fixed_width=1024)
        """
        self.fixed_width = kwargs['fixed_width'] if 'fixed_width' in kwargs \
            else self.DEFAULT_RESIZED_WIDTH
        self.fixed_height = kwargs['fixed_height'] if 'fixed_height' in kwargs \
            else self.DEFAULT_RESIZED_HEIGHT
        self.img_from_path = img_from

        self.__compress__()

        # se crea redimensionada renombrada a .p
        self.img_resized_path = self.__rename_to_p_jpg__(self.img_compressed_path)
        self.img = Image.open(self.img_compressed_path)
        self.img_width = self.img.size[0]
        self.img_height = self.img.size[1]

        if self.img_width >= self.img_height:
            self.__resize_width__()
        else:
            self.__resize_height__()

        # si se ha redimensionado se guarda la redimensionada, si no, entonces
        # se guarda la misma que la comprimida pero con el .p
        if hasattr(self, 'img_resized'):
            self.img_resized.save(self.img_resized_path)
        else:
            self.img.save(self.img_resized_path)

        # si hay algun archivo que no esté dentro de la lista se elimina
        if common.UNIT_TEST_MODE:
            filename = self.__get_filename__(self.img_from_path)
            path = os.path.join(TEST_IMGS_COPIES_PATH, filename)
            os.remove(path)

        return self.img_resized_path


class S3BucketHandler:
    # set boto lib debug to critical
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    # connect to the bucket
    conn = boto.connect_s3(common.AWS_ACCESS_KEY_ID, common.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(common.BUCKET_NAME)

    @classmethod
    def push_file(cls, fn, file_id, from_file_object=False):
        """
        file_id: para identificar el archivo dentro del bucket
        """
        # create a key to keep track of our file in the storage
        k = Key(cls.bucket)
        k.key = file_id
        if from_file_object:
            k.set_contents_from_file(fn)
        else:
            k.set_contents_from_filename(fn)
            # remove the file from the web server
            os.remove(fn)
        # we need to make it public so it can be accessed publicly
        # using a URL like http://s3.amazonaws.com/bucket_name/key
        # http://scandaloh.s3.amazonaws.com/prueba.png
        k.make_public()

    @classmethod
    def remove_file(cls, file_id):
        "Quita archivo del bucket"
        k = Key(cls.bucket)
        k.key = file_id
        cls.bucket.delete_key(k)

    @classmethod
    def make_backup(cls):
        """
        Hace copia de seguridad en LOCAL_PATH de todos los archivos
        alojados en el bucket
        """
        bucket_list = cls.bucket.list()
        for l in bucket_list:
            keyString = str(l.key)
            # check if file exists locally, if not: download it
            if not os.path.exists(common.LOCAL_PATH + keyString):
                l.get_contents_to_filename(common.LOCAL_PATH + keyString)




#
# Operaciones cadenas para archivos
#
def change_directory(path_to_filename, path_to_desired_dir):
    """
    Dada una cadena con el path abs de un archivo, se cambia para que este archivo
    apunte al directorio abs deseado

    e.g. /path/to/file1.jpg -> /another/path/to/file1.jpg
    """
    filename = re.sub(r'^.*\/(.*\..*)$', r'\1', path_to_filename)
    return os.path.join(path_to_desired_dir, filename)


def rename_extension(filename, ext):
    return re.sub(r'^(.*)\..*$', r'\1.' + ext, filename)


def get_extension(filename):
    return re.sub(r'^.*\.(.*)$', r'\1', filename)


def rename_to_p(filename):
    "e.g. foto_1.jpg -> foto_1.p.jpg"
    return re.sub(r'(?:_a)?\.([^.]*)$', r'.p.\1', filename)
