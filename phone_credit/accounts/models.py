from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    
    

class SellerCredit(models.Model):
    seller = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    credit = models.BigIntegerField(default=0)
    freezed_credit = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.seller}: credit amount {self.credit}"