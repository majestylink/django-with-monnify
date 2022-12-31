from django.contrib.auth.models import User
from django.db import models


class Base(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Book(Base):
    title = models.CharField(max_length=100, null=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    isbn = models.CharField(max_length=50, null=True, blank=True)


class OrderPayment(Base):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
