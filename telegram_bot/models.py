from django.db import models
from core.models import TimeStampedModel



class TgUser(TimeStampedModel):
    user_id = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.user_id)