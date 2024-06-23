from django.contrib import admin

# Register your models here.
from .models import Loan,Dues
admin.site.register(Loan)
admin.site.register(Dues)
