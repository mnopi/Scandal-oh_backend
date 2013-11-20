import os
import datetime
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from services import models
import factory
from factory import DjangoModelFactory
from settings.common import TEST_SOUNDS_PATH


class CustomUserFactory(DjangoModelFactory):
    FACTORY_FOR = models.CustomUser

    username = factory.Sequence(lambda n: 'user_%s' % n)
    password = '1234'


class FacebookUserFactory(DjangoModelFactory):
    FACTORY_FOR = models.CustomUser

    username = factory.Sequence(lambda n: 'facebook_user_%s' % n)
    social_network = 1


class CategoryFactory(DjangoModelFactory):
    FACTORY_FOR = models.Category

    name = factory.Sequence(lambda n: 'category_%s' % n)


class PhotoFactory(DjangoModelFactory):
    FACTORY_FOR = models.Photo

    title = factory.Sequence(lambda n: 'title_%s' % n)
    user = factory.SubFactory(CustomUserFactory)
    category = factory.SubFactory(CategoryFactory)
    img = factory.django.ImageField(color='green')
    sound = factory.django.FileField(filename=os.path.join(TEST_SOUNDS_PATH, 'prueba de sonido.3gp'))

    @factory.post_generation
    def for_list(self, create, extracted, **kwargs):
        """
        Generamos una lista de fotos con diferentes fechas, en este caso aparecen
        8 fotos, subidas cada 3 meses
        """
        if extracted:
            num_photos = 8
            month_interval = 3
            base = datetime.datetime.today()
            dateList = [base - relativedelta(months=x*month_interval)
                        for x in range(0, num_photos)]
            for d in dateList:
                PhotoFactory(date=d)


class CommentFactory(DjangoModelFactory):
    FACTORY_FOR = models.Comment

    user = factory.SubFactory(CustomUserFactory)
    photo = factory.SubFactory(PhotoFactory)
    text = factory.Sequence(lambda n: 'this is comment_%s, bla bla blahh' % n)
    date = factory.LazyAttribute(lambda x: now())