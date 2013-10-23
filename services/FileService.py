# -*- coding: utf-8 -*-

import os
from django.core.files.base import ContentFile
from factory_model import CLASSES


class FileService:
    """
    Helper para construir web services que manipulen el archivo de un recurso dado:
        /api-2/[resource]/[id]/file

    Por ejemplo, para el recurso 'photo' con id=16:
        - Subir archivo de la foto:
            POST > /services/photo/16/file
        - Eliminar archivo:
            DELETE > /services/photo/16/file
    """
    model_file_attr = None

    def __init__(self, request, resource, id):
        self.request = request
        self.resource = resource
        self.id = id
        self.resource_class = CLASSES[resource]

    def upload_file(self, uploaded_file):
        """
        Sube el archivo para el recurso. Si ya hay una imágen ésta se elimina
        """
        file_content = ContentFile(uploaded_file.read())

        # Xej photo: resource_obj = Photo.objects.get(id=self.id)
        resource_obj = self.resource_class.objects.get(id=self.id)

        # Se elimina el archivo que el recurso tenía antes
        # nombre para el atributo donde queremos subir el archivo (img, img_small,..)
        file_name = uploaded_file.field_name
        self.model_file_attr = getattr(resource_obj, file_name)
        if self.model_file_attr.name:
            storage, path = self.model_file_attr.storage, self.model_file_attr.path
            storage.delete(path)

        # Guardamos la nueva imágen
        filename = uploaded_file.name.replace(" ", "_")
        fileName, fileExtension = os.path.splitext(filename)
        fileName = str(resource_obj.id) + fileExtension
        self.model_file_attr.save(fileName, file_content)
        resource_obj.save()


    def delete_file(self):
        """
        Elimina el archivo para el recurso
        """
        obj = self.resource_class.objects.get(id=self.id)
        self.model_file_attr = getattr(obj, self.request.GET.get('field'))
        # You have to prepare what you need before delete the model
        storage, path = self.model_file_attr.storage, self.model_file_attr.path
        # Delete the model before the file
        # super(ObjectType, self).delete(*args, **kwargs)
        # # Delete the file after the model
        # print path
        storage.delete(path)

        # deja nulo el campo para la imágen
        setattr(obj, self.request.GET.get('field'), None)
        obj.save()