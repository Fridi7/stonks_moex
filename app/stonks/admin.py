from django.contrib import admin

from .models import Stock, QuotedSecurities

admin.site.register(Stock)
admin.site.register(QuotedSecurities)
