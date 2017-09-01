# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Category(models.Model):
    category_name = models.CharField(max_length=255, null=False, unique=True, default='')
    # separated by ,
    keywords = models.CharField(max_length=2048, null=False, unique=True)
    url = models.CharField(max_length=2048, null=False, unique=True)

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.keywords)

class Paper(models.Model):
    """This class represents the PubMed's paper model."""
    uid = models.CharField(max_length=10, null=False, unique=True)

    pubdate = models.CharField(max_length=255, null=True, unique=False)
    source = models.CharField(max_length=255, null=True, unique=False)
    authors = models.CharField(max_length=2048, null=True, unique=False)
    title = models.CharField(max_length=2048, null=True, unique=False)
    sortpubdate = models.CharField(max_length=255, null=True, unique=False)

    year = models.IntegerField(null=True, default=0)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True,)

    def __str__(self):
        """Return a human readable representation of the model instance."""
        return "{}".format(self.uid)
