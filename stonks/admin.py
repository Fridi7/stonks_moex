from django.contrib import admin

# Register your models here.
from .models import Stock, QuotedSecurities
admin.site.register(Stock)
admin.site.register(QuotedSecurities)
