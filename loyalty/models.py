from datetime import datetime, timedelta


from django.db import models
from django.forms import ValidationError


class ExpireTerms(models.Choices):
    ONE_MINUTE = "1 minute"
    FIVE_MINUTES = "5 minutes"
    ONE_HOUR = "1 hour"

    @classmethod
    def validate_and_calc_expire_at(cls, expire_term: 'ExpireTerms') -> datetime:
        if expire_term == ExpireTerms.ONE_MINUTE.value:
            delta = timedelta(minutes=1)
        elif expire_term == ExpireTerms.FIVE_MINUTES.value:
            delta = timedelta(minutes=5)
        elif expire_term == ExpireTerms.ONE_HOUR.value:
            delta = timedelta(hours=1)
        else:
            raise ValidationError("Invalid expire term")

        return datetime.now() + delta

class CardStatus(models.Choices):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    EXPIRED = 'expired'


class Card(models.Model):
    series = models.CharField(max_length=5)
    number = models.CharField(unique=True, max_length=10)
    status = models.CharField(max_length=10, choices=CardStatus.choices)
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f'Card [{self.series}-{self.number}]'

    class Meta:
        ordering = ['-issued_at']

    def is_inactive(self) -> bool:
        return self.status == CardStatus.INACTIVE.value

    def is_expired(self) -> bool:
        return self.status == CardStatus.EXPIRED.value


class Transaction(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateTimeField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-date']
