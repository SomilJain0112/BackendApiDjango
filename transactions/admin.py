from django.contrib import admin

# Register your models here.
from .models import Transaction,Billing
admin.site.register(Transaction)
admin.site.register(Billing)