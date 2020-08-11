from django.db import models


class QuotedSecurities(models.Model):
    trade_data = models.DateField()
    secid = models.CharField(max_length=36)
    name = models.CharField(max_length=765)
    isin = models.CharField(max_length=765)
    reg_number = models.CharField(max_length=189, blank=True, null=True)
    main_board_id = models.CharField(max_length=12, blank=True, null=True)
    list_level = models.CharField(max_length=6, blank=True, null=True)
    quoted = models.BooleanField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["pk"]


class Stock(models.Model):
    secid = models.ForeignKey('QuotedSecurities', related_name='stocks', on_delete=models.CASCADE)
    trade_data = models.DateField()
    close = models.FloatField(null=True)
    name = models.CharField(max_length=765)
    board_id = models.CharField(max_length=12, null=True)

    def __str__(self):
        return str(self.close)
