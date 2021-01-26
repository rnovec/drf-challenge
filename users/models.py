from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

from .managers import UserManager

# Create your models here.


class Organization(models.Model):
    name = models.CharField(default='', max_length=30, blank=True)
    phone = models.CharField(default='', max_length=20, blank=True)
    address = models.CharField(default='', max_length=100, blank=True)

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('full name'), max_length=30, blank=True)
    birthdate = models.DateTimeField(_('birthdate'), null=True, blank=True)
    phone = models.CharField(_('phone'), max_length=20, null=True, blank=True)

    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    organization = models.ForeignKey(
        Organization, null=True, blank=True, on_delete=models.SET_NULL)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
