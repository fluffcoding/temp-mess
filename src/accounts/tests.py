from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import *
import random
import datetime


class MoneyHandlerTest(TestCase):

    def setUp(self):
        user = get_user_model().objects.create_user(
            email="user1@iba.edu.pk", password="fooooo0000", erp=19334)
        user2 = get_user_model().objects.create_user(
            email="user2@iba.edu.pk", password="fooooo0000", erp=19335)
        user3 = get_user_model().objects.create_user(
            email="user3@iba.edu.pk", password="fooooo0000", erp=19336)

        self.balance_user_1 = random.randint(5000, 15000)
        self.balance_user_2 = random.randint(5000, 15000)
        self.balance_user_3 = random.randint(5000, 15000)

        MessAccount.objects.topup_wallet(
            amount=self.balance_user_1, user=user
        )
        MessAccount.objects.topup_wallet(
            amount=self.balance_user_2, user=user2
        )
        MessAccount.objects.topup_wallet(
            amount=self.balance_user_3, user=user3
        )

    def test_messaccount_entries_for_topups(self):
        accounts = MessAccount.objects.all()
        self.assertEqual(
            accounts[0].balance, 0, "The first row in of the mess balance is not zero")
        self.assertEqual(accounts[1].balance, accounts[0].balance +
                         accounts[1].amount, "the math does not addup")
        self.assertEqual(accounts[2].balance, accounts[1].balance +
                         accounts[2].amount, "the math does not addup")
        self.assertEqual(accounts[3].balance, accounts[2].balance +
                         accounts[3].amount, "the math does not addup")

        last_entry = MessAccount.objects.last()
        self.assertEqual(last_entry.balance, (self.balance_user_1 +
                         self.balance_user_2+self.balance_user_3))

    def test_wallet_balances(self):
        wallet_1 = Wallet.objects.get(user__email="user1@iba.edu.pk")
        self.assertEqual(wallet_1.balance, self.balance_user_1)

        wallet_2 = Wallet.objects.get(user__email="user2@iba.edu.pk")
        self.assertEqual(wallet_2.balance, self.balance_user_2)

        wallet_3 = Wallet.objects.get(user__email="user3@iba.edu.pk")
        self.assertEqual(wallet_3.balance, self.balance_user_3)

    def test_inventory_addition(self):
        price = random.randint(1000, 10000)

        MessAccount.objects.add_inventory(
            "Chiken",
            23,
            "KG",
            price
        )

        self.assertRaises(ValueError, MessAccount.objects.add_inventory, *[
            "Aaata",
            23,
            "kilo",
            2000
        ])

        last_entry = MessAccount.objects.last()
        balance = self.balance_user_1 + self.balance_user_2 + self.balance_user_3
        adjust = balance - price
        self.assertEqual(last_entry.balance, adjust)


class WalletTests(TestCase):

    def setUp(self) -> None:
        user = get_user_model().objects.create_user(
            email="user1@iba.edu.pk", password="fooooo0000", erp=19334)
        user2 = get_user_model().objects.create_user(
            email="user2@iba.edu.pk", password="fooooo0000", erp=19335)
        user3 = get_user_model().objects.create_user(
            email="user3@iba.edu.pk", password="fooooo0000", erp=19336)

        price = Price.objects.create(
            dinner=210,
            lunch=200,
            breakfast=180,
            surcharge=500
        )

        period_model = apps.get_model("subscription", "Period")
        period_model.objects.create(
            end_date=datetime.date(2023, 3, 28)
        )
        user.subscribe(dinner=True)
        user2.subscribe(lunch=True)
        user3.subscribe(breakfast=True)

        return super().setUp()

    def test_(self):
        pass
