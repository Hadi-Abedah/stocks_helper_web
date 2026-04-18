from django.contrib import admin
from .models import Transaction, Journal
# Register your models here.
admin.site.register(Transaction)
admin.site.register(Journal)