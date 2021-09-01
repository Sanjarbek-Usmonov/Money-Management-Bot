from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    tg_user = models.OneToOneField('telegram_bot.TgUser', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.id}'


class Wallet(models.Model):
    profile = models.OneToOneField('Profile', on_delete=models.SET_NULL, null=True)
    balance = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.id}'


class Category(models.Model):
    user = models.OneToOneField('Profile', on_delete=models.SET_NULL, null=True)
    food = models.IntegerField(default=0)
    transport = models.IntegerField(default=0)
    clothes = models.IntegerField(default=0)
    taxes = models.IntegerField(default=0)
    extra_payments = models.IntegerField(default=0)
    other = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.id}'