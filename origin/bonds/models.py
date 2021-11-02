from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Bond(models.Model):
    isin = models.CharField(max_length=40, null=False)
    size = models.BigIntegerField(null=False)
    currency = models.CharField(max_length=3, null=False)
    maturity = models.DateField(null=False)
    lei = models.CharField(max_length=40, null=False)
    legal_name = models.CharField(max_length=40)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.legal_name
