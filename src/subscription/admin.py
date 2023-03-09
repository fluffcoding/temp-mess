from django.contrib import admin

# Register your models here.

from .models import Subscription, Period


admin.site.register(Subscription)
admin.site.register(Period)