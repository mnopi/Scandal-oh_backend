# -*- coding: utf-8 -*-
import re

from django.contrib.auth.models import User
from tastypie.authorization import Authorization
from tastypie.exceptions import Unauthorized
from services.factory_model import CLASSES
from services.models import CustomUser


class ResourceAuthorization(Authorization):
    """
    Clase para autorizar las operaciones CRUD sobre cada recurso de la API 1

    http://django-tastypie.readthedocs.org/en/latest/authorization.html
    """

    RESOURCES_WITH_GET_ALLOWED = [
        'user',
        'photo',
        'category',
        'comment',
    ]

    # Para indicar si un registro para el recurso ha sido creado justo antes
    # de realizar su lectura
    resource_created = False

    def __init__(self, rel_to_user):
        """
        Le metemos la ruta a seguir en el esquema relacional hasta llegar al usuario
        (owner del enclosure).

        Por ejemplo para llegar desde EnclosureResource:
            authorization = ResourceAuthorization('owner')
        Desde LabelCategoryResource:
            authorization = ResourceAuthorization('enclosure__owner')
        """
        self.rel_to_user = rel_to_user

    def __has_get_method_allowed__(self):
        return self.resource_meta.resource_name in self.RESOURCES_WITH_GET_ALLOWED

    def __get_id_from_uri__(self, uri):
        """
        Por ejemplo, de /api/v1/enclosure/27/, devolverá 27
        """
        return re.search(r".*\/(\d+)/.*", uri).group(1)

    def __bundle_owner_match_to_user__(self, bundle):
        """
        Comprueba que el dueño del elemento es el mismo que el usuario que lo crea,
        a menos que sea miembro del staff. Así evitamos que por ejemplo un dueño
        pueda crear recintos para otros dueños.
        """
        if bundle.request.user.is_staff:
            return True

        owner_id = self.__get_id_from_uri__(bundle.data['owner'])
        if bundle.request.user.is_authenticated() and bundle.request.user.id == long(owner_id):
            return True

        return False


    def __user_can_access__(self, bundle):
        """
        Determina si un usuario tiene permiso para acceder al recurso dado y realizar operaciones:
            - GET
            - PUT
            - DELETE
        """
        if bundle.request.user.is_staff:
            return True

        if type(bundle.obj) is CustomUser:
            return bundle.obj.id == bundle.request.user.id

        # Vamos iterando en cada uno de los elementos que nos llevan hasta owner.
        # Por ejemplo, para LabelCategory:
        #   'enclosure__owner' -> ['enclosure', 'owner'],
        #   lo que crearía esta comparación:
        #       bundle.obj.enclosure.owner == bundle.request.user
        attrs = self.rel_to_user.split('__')
        value = bundle.obj
        for i in range(len(attrs)):
            if value is None:
                break
            value = getattr(value, attrs[i])

        return value == bundle.request.user


    def __user_can_create__(self, bundle):
        """
        Determina si el usuario que hace la petición tiene permiso para crear el recurso.

        Por ejemplo, si el usuario no es dueño de un enclosure con id=37, entonces tampoco
        podrá crear una planta para dicho enclosure, por ejemplo:
            {"name":"floor_1","enclosure":"/api/v1/enclosure/37/"}

        Asímismo, si el usuario no es staff y crea un floor sin especificar su enclosure,
        entonces no estará autorizado para crearlo.
        """
        if bundle.request.user.is_staff:
            return True

        attrs = self.rel_to_user.split('__') # 'enclosure__owner' => ['enclosure, 'owner']
        direct_rel = attrs[0] # 'enclosure'

        # Si no especificamos enclosure para el floor
        if not direct_rel in bundle.data:
            return False

        # Me quedo con el enclosure para el que quiero crear la planta,
        # es decir, de 'enclosure__owner' me quedo con 'enclosure'.
        # Comprobamos que ese recinto pertenece al usuario
        direct_rel_id = self.__get_id_from_uri__(bundle.data[direct_rel]) # 37
        direct_rel_obj = CLASSES[direct_rel].objects.get(id=direct_rel_id) # objeto Enclosure con id=37

        # Para este mismo caso de floor el siguiente attr es 'owner'
        value = direct_rel_obj
        for i in range(len(attrs)-1):
            if value is None:
                break
            value = getattr(value, attrs[i+1])

        return value == bundle.request.user

    def read_list(self, object_list, bundle):
        """
        Para leer una lista de elementos para el recurso
        """
        if self.__has_get_method_allowed__():
            return object_list

        # # Si lo que estamos pidiendo es la lista de usuarios:
        # if type(bundle.obj) is CustomUser:
        #     return object_list.filter(id=bundle.request.user.id)
        #
        # # Si el usuario no está logueado
        # if not bundle.request.user.is_authenticated():
        #     return []
        #
        # # Para el resto de casos, por ejemplo un user con id 2 que hace consulta sobre floor:
        # #       object_list.filter(enclosure__owner)
        # return object_list.filter(**{self.rel_to_user:bundle.request.user})

    def read_detail(self, object_list, bundle):
        """
        Para leer un elemento del recurso.

        Sea cual sea el recurso, se podrá leer cuando:
            - Se pueda hacer GET sobre él (esté en RESOURCES_WITH_GET_ALLOWED)
            - Se acabe de crear o editar un recurso (cuando llama luego a esta función
              para devolver los datos sobre el creado)
        """
        # if self.__has_get_method_allowed__() or self.__class__.resource_created:
        #     self.__class__.resource_created = False
        #     return True
        #
        # return self.__user_can_access__(bundle)
        return True

    # def create_list(self, object_list, bundle):
    #     # Assuming their auto-assigned to ``user``.
    #     return object_list

    def create_detail(self, object_list, bundle):
        # # return bundle.obj.user == bundle.request.user
        # self.__class__.resource_created = True
        #
        # # Si el elemento contiene información sobre su dueño (owner)..
        # if 'owner' in bundle.data:
        #     return self.__bundle_owner_match_to_user__(bundle)
        #
        # # Para comprobar que se está creando algo sobre un elemento del usuario
        # return self.__user_can_create__(bundle)
        return True

    # def update_list(self, object_list, bundle):
    #     allowed = []
    #
    #     # Since they may not all be saved, iterate over them.
    #     for obj in object_list:
    #         if obj.user == bundle.request.user:
    #             allowed.append(obj)
    #
    #     return allowed

    def update_detail(self, object_list, bundle):
        # return self.__user_can_access__(bundle)
        return True

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        return self.__user_can_access__(bundle)