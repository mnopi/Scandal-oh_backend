from services import models
import factory
from factory import DjangoModelFactory


class CustomUserFactory(DjangoModelFactory):
    FACTORY_FOR = models.CustomUser

    username = factory.Sequence(lambda n: 'user_%s' % n)
    password = '1234'


class CategoryFactory(DjangoModelFactory):
    FACTORY_FOR = models.Category

    name = factory.Sequence(lambda n: 'category_%s' % n)


