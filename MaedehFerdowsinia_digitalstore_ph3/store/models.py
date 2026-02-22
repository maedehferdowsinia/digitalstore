from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class FileQuerySet(models.QuerySet):
    def available(self):
        return self.all()

    def by_seller(self, seller):
        return self.filter(seller=seller)

    def purchased_by(self, user):
        return self.filter(
            orderitem__order__buyer=user,
            orderitem__order__is_paid=True
        ).distinct()


class FileManager(models.Manager):
    def get_queryset(self):
        return FileQuerySet(self.model, using=self._db)

    def available(self):
        return self.get_queryset().available()

    def by_seller(self, seller):
        return self.get_queryset().by_seller(seller)

    def purchased_by(self, user):
        return self.get_queryset().purchased_by(user)


class OrderItemManager(models.Manager):
    def purchased_by(self, user):
        return self.filter(
            order__buyer=user,
            order__is_paid=True
        ).select_related('file', 'order')




class File(models.Model):

    FILE_TYPES = [
        ('image', 'Image'),
        ('music', 'Music'),
        ('book', 'Book'),
        ('article', 'Article'),
    ]

    objects = FileManager()

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    title = models.CharField(max_length=200)
    description = models.TextField()
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Article(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='article')
    keywords = models.CharField(max_length=300)
    pages = models.PositiveIntegerField()


class Book(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='book')
    author = models.CharField(max_length=100)
    pages = models.PositiveIntegerField()


class Music(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='music')
    duration = models.DurationField()
    format = models.CharField(max_length=50)


class Image(models.Model):
    file = models.OneToOneField(File, on_delete=models.CASCADE, related_name='image')
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    format = models.CharField(max_length=20)



class Order(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    file = models.ForeignKey(File, on_delete=models.CASCADE)

    objects = OrderItemManager()



