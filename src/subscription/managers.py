from django.db import models
from django.apps import apps
import datetime


class PeriodManager(models.Manager):
    def create(self, **kwargs):
        Price = apps.get_model("accounts", "Price")
        currently_active_period = self.model.objects.filter(is_active=True)
        currently_active_pricing = Price.objects.filter(is_active=True)

        if not currently_active_pricing.exists():
            raise ValueError("Create pricings for this period")

        kwargs.setdefault("prices", currently_active_pricing[0])

        if currently_active_period.exists():
            currently_active_period.update(is_active=False)

        period = super().create(**kwargs)
        # TODO close the period here
        return period


class SubscriptionManager(models.Manager):
    def create(self, **kwargs):
        user = kwargs.get("user")
        subscription_model = self.model
        subscriptions = subscription_model.objects.filter(
            user=user, is_active=True)
        if subscriptions.exists():
            subscriptions.update(is_active=False)
        period_model = apps.get_model("subscription", "Period")
        try:
            active_period = period_model.objects.get(is_active=True)
        except period_model.DoesNotExist:
            raise ValueError(
                "Create a period and price before you can create a subscription")

        if not datetime.date.today() < active_period.end_date:
            active_period.is_active = False
            active_period.save()
            raise ValueError(
                f"the cuurrently active period has ended on {str(active_period.end_date)} please start a new period. \nThe period has been de activated")

        kwargs.setdefault("period", active_period)
        return super().create(**kwargs)


class WalletManager(models.Manager):
    pass
