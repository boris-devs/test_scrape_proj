from django.db import models


class Currency(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)


class CurrencyRate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=12, decimal_places=8)
    date = models.DateField(db_index=True)
