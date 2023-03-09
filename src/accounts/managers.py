from django.db import models
from django.apps import apps

WALLET = 0
INVENTORY = 1
EXPENSES = 2
ADJUSTMENT = 3


class PriceManager(models.Manager):

    def create(self, **kwargs):
        currently_active_pricing = self.model.objects.filter(is_active=True)
        if currently_active_pricing.exists():
            currently_active_pricing.update(is_active=False)

        return super().create(**kwargs)


class MessAccountManager(models.Manager):
    def create(self, **kwargs):
        return super().create(**kwargs)

    def __last_entry(self, default_type=0):

        last_row = self\
            .filter(created_at__isnull=False)

        if not last_row.exists():
            new_row = self.create(
                balance=0,
                transact_with=0,
                of_type=default_type,
                amount=0,
                counter_entry=0
            )
            return new_row

        last_row = self\
            .filter(created_at__isnull=False) \
            .latest("created_at")
        return last_row

    def __debit(self, amount, transact_with, counter_entry):
        last_row = self.__last_entry()
        balance = last_row.balance + amount
        of_type = self.model.DEBIT

        self.create(
            balance=balance,
            transact_with=transact_with,
            of_type=of_type,
            amount=amount,
            counter_entry=counter_entry
        )

    def __credit(self, amount, transact_with, counter_entry):
        last_row = self.__last_entry()
        balance = last_row.balance - amount
        of_type = self.model.CREDIT

        self.create(
            balance=balance,
            transact_with=transact_with,
            of_type=of_type,
            amount=amount,
            counter_entry=counter_entry
        )

    def topup_wallet(self, user, amount=0):
        if amount != 0:
            # add money to the wallet
            wallet_model = apps.get_model("accounts", "Wallet")
            wallet = wallet_model.objects.get(user=user)
            wallet.debit(amount=amount)
            wallet.save()

            # creates a new row for addition to the mess
            self.__debit(amount, WALLET, wallet.pk)

    def add_inventory(self, name, quantity, unit, price, receipt=None):
        # added the inventory
        try:
            per_item = price/quantity
        except ZeroDivisionError:
            raise ZeroDivisionError(
                "The quantity for inventory cannot be zero")

        inventory_model = apps.get_model("accounts", "Inventory")

        if unit not in inventory_model.UNITS.values:
            raise ValueError(
                f"units can only be from {inventory_model.UNITS.values}")

        added_inventory = inventory_model.objects.create(
            item_price_total=price,
            item_quantity=quantity,
            item_name=name,
            item_price_per_unit=per_item,
            receipt=receipt,
            unit=unit
        )

        # credit the mess account
        self.__credit(price, INVENTORY, added_inventory.pk)
