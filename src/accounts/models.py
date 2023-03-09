from django.db import models
from django.contrib.auth import get_user_model
from .managers import PriceManager, MessAccountManager
from django.apps import apps


class Wallet(models.Model):
    # just a breakdown of all the payabes per user
    # seprate for each student the balances are updated with time or user action
    balance = models.IntegerField(default=0)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def credit(self):
        # happens every 24hr and decreases the Wallet but increases the Revenue
        Subscription = apps.get_model("accounts", "Subscription")
        active_subscription = Subscription.objects.get(
            is_active=True, user=self.user)
        total_payment = active_subscription.get_total_payment()
        total_days = active_subscription.get_days()
        self.balance = self.balance - (total_payment/total_days)
        self.save()

    def debit(self, amount=0):
        # increases the balance in the wallet and increase the mess account
        mess_account = apps.get_model("accounts", "MessAccount")
        if amount > 0:
            self.balance = self.balance + amount
            self.save()
        else:
            raise ValueError(
                "All amount entered to the debit must be non zero")


class MessAccount(models.Model):
    # breakdown of all the liquid asset the mess has
    # is a detailed ledger of all the transactions
    # that happen to in the mess account

    WALLET = 0
    INVENTORY = 1
    EXPENSES = 2
    ADJUSTMENT = 3

    FROM_CHOICES = (
        (WALLET, "WALLET"),
        (INVENTORY, "INVENTORY"),
        (EXPENSES, "EXPENSES"),
        (ADJUSTMENT, "ADJUSTMENT")
    )
    CREDIT = 1
    DEBIT = 0
    OF_TYPE = (
        (CREDIT, "CREDIT"),
        (DEBIT, "DEBIT")
    )

    balance = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    transact_with = models.IntegerField(choices=FROM_CHOICES)
    counter_entry = models.IntegerField()
    of_type = models.IntegerField(choices=OF_TYPE)
    amount = models.IntegerField()

    objects = MessAccountManager()


class Revenue(models.Model):
    CREDIT = 1
    DEBIT = 0
    OF_TYPE = (
        (CREDIT, "CREDIT"),
        (DEBIT, "DEBIT")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    of_type = models.IntegerField(choices=OF_TYPE)


class UNITS(models.TextChoices):
    Kilo_Grams = "KG"
    Grams = "G"
    Pieces = "P"
    Litters = "L"


class Inventory(models.Model):
    UNITS = UNITS

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="Unit_Constraint",
                check=models.Q(unit__in=UNITS.values),
            )
        ]

    created_at = models.DateTimeField(auto_now_add=True)
    item_price_total = models.IntegerField()
    item_price_per_unit = models.IntegerField()
    item_quantity = models.IntegerField()
    item_name = models.CharField(max_length=100)
    receipt = models.ImageField(upload_to=f"receipts/", null=True, blank=True)
    unit = models.CharField(max_length=10, choices=UNITS.choices)

    # when ever this account gets credited it is transferred to the revenue

    # when ever this account is debited it has to credit the cash


class Price(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    dinner = models.IntegerField()
    lunch = models.IntegerField()
    breakfast = models.IntegerField()
    surcharge = models.IntegerField()
    is_active = models.BooleanField(default=True)

    objects = PriceManager()
