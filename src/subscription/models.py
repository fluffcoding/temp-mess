from django.db import models
from django.contrib.auth import get_user_model
from .managers import *
import datetime
import warnings
from django.apps import apps


class Period(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    end_date = models.DateField()
    prices = models.ForeignKey("accounts.Price", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    objects = PeriodManager()


class Subscription(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)
    dinner = models.BooleanField(default=False)
    lunch = models.BooleanField(default=False)
    breakfast = models.BooleanField(default=False)
    terminated_at = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    objects = SubscriptionManager()


    def __str__(self):
        return self.user.email + ' - ' + str(self.is_active)


    def get_days(self):
        if self.terminated_at == None:
            end = self.period.end_date
        else:
            end = self.terminated_at
        start = self.created_at
        return end - start

    def get_total_payment(self, detail=False, total_days=None):
        breakdown = {}
        # TODO add "past_balance"

        if self.dinner:
            breakdown["availing_dinner"] = True
            breakdown["dinner_price"] = self.period.prices.dinner

        if self.lunch:
            breakdown["availing_lunch"] = True
            breakdown["lunch_price"] = self.period.prices.lunch

        if self.breakfast:
            breakdown["availing_breakfast"] = True
            breakdown["breakfast_price"] = self.period.prices.breakfast

        price_filter = filter(None, [
            breakdown["dinner_price"],
            breakdown["lunch_price"],
            breakdown["breakfast_price"]
        ])
        total_per_day = sum(price_filter)
        if total_days == None:
            total_days = self.get_days().days
        breakdown["days"] = total_days

        breakdown["charge_for_dinner"] = total_days * breakdown["dinner_price"]
        breakdown["charge_for_lunch"] = total_days * breakdown["lunch_price"]
        breakdown["charge_for_breakfast"] = total_days * \
            breakdown["breakfast_price"]

        breakdown["surcharge_added"] = False
        if len(list(price_filter)) == 1:
            breakdown["surcharge_added"] = True
            breakdown["surcharge"] = self.period.prices.surcharge
        breakdown["total"] = total_days * total_per_day
        if detail:
            return breakdown
        return breakdown["total"]

    def terminate(self, force=False):
        if self.terminated_at == None or force:
            termination_date = datetime.date.today()
            self.terminated_at = termination_date
            self.is_active = False
            self.save()
        else:
            warnings.warn(
                "Trying to set the termination date on an already terminated subscription. use force=True")
