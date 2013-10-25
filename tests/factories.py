from django.utils.timezone import now
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


class PhotoFactory(DjangoModelFactory):
    FACTORY_FOR = models.Photo

    title = factory.Sequence(lambda n: 'title_%s' % n)
    user = factory.SubFactory(CustomUserFactory)
    category = factory.SubFactory(CategoryFactory)
    img = factory.django.ImageField(color='green')


class CommentFactory(DjangoModelFactory):
    FACTORY_FOR = models.Comment

    user = factory.SubFactory(CustomUserFactory)
    photo = factory.SubFactory(PhotoFactory)
    text = factory.Sequence(lambda n: 'this is comment_%s, bla bla blahh' % n)
    date = factory.LazyAttribute(lambda x: now())