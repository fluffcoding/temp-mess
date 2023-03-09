from django.test import TestCase
from django.contrib.auth import get_user_model
import datetime
from django.core.exceptions import ValidationError
from django.apps import apps

Price = apps.get_model("accounts", "Price")
Period = apps.get_model("subscription", "Period")
Subscription = apps.get_model("subscription", "Subscription")


class PriceTester(TestCase):

    def setUp(self):
        Price.objects.create(breakfast=180, lunch=124,
                             dinner=1234, surcharge=124)
        Price.objects.create(breakfast=34, lunch=1212,
                             dinner=1234, surcharge=124)
        Price.objects.create(breakfast=3123, lunch=124,
                             dinner=3456, surcharge=234)
        Price.objects.create(breakfast=134, lunch=123,
                             dinner=234, surcharge=2354)
        Price.objects.create(breakfast=2312, lunch=1234,
                             dinner=123, surcharge=23)
        Price.objects.create(breakfast=235, lunch=123,
                             dinner=123, surcharge=234)
        Price.objects.create(breakfast=124, lunch=2345,
                             dinner=56, surcharge=346)
        Price.objects.create(breakfast=124, lunch=1234,
                             dinner=33, surcharge=123)
        Price.objects.create(breakfast=124, lunch=1234,
                             dinner=543, surcharge=333)
        Price.objects.create(breakfast=124, lunch=2345,
                             dinner=56, surcharge=346)

    def test_price_attributes(self):
        price = Price.objects.all()

        self.assertFalse(price[0].is_active)
        self.assertFalse(price[1].is_active)
        self.assertFalse(price[2].is_active)
        self.assertFalse(price[3].is_active)
        self.assertFalse(price[4].is_active)
        self.assertFalse(price[5].is_active)
        self.assertFalse(price[6].is_active)
        self.assertFalse(price[7].is_active)
        self.assertFalse(price[8].is_active)

        self.assertTrue(price[9].is_active)


class PeriodTester(TestCase):

    def setUp(self):
        end_date = datetime.datetime(2023, 3, 14)
        self.assertRaises(ValueError, Period.objects.create,
                          **{"end_date": end_date})

    def test_period_creation(self):
        # multiple price tables created only the last one is
        # active and working and is assigned to any period created

        end_date = datetime.date(2023, 3, 14)
        Price.objects.create(breakfast=180, lunch=200,
                             dinner=210, surcharge=501)
        Price.objects.create(breakfast=180, lunch=200,
                             dinner=210, surcharge=502)

        price = Price.objects.create(
            breakfast=180, lunch=200, dinner=210, surcharge=503)
        period = Period.objects.create(end_date=end_date)

        self.assertEqual(price.surcharge, period.prices.surcharge)


class SubscriptionTester(TestCase):
    User = get_user_model()

    def setUp(self):
        Price.objects.create(breakfast=180, lunch=124,
                             dinner=1234, surcharge=502)
        Price.objects.create(breakfast=180, lunch=200,
                             dinner=210, surcharge=501)
        self.end_date = datetime.date(2023, 3, 14)
        Period.objects.create(end_date=self.end_date)
        try:
            self.User.objects.create_user(
                "student@khi.iba.edu.pk", "fooooooo", erp=19334)
        except ValidationError as e:
            self.fail("non admin non student user creation failed")

    def test_subscription_to_stale_period(self):
        Period.objects.create(end_date=datetime.date(2023, 2, 14))
        user = self.User.objects.get(email="student@khi.iba.edu.pk")
        self.assertRaises(ValueError, user.subscribe, **{"breakfast": True})

    def test_the_days(self):
        # get the active period and prices
        period = Period.objects.get(is_active=True)
        price = Price.objects.get(is_active=True)

        # get a created user
        user = self.User.objects.get(email="student@khi.iba.edu.pk")

        # check if the prices have correctly been assigned
        self.assertEqual(period.prices.surcharge, price.surcharge,
                         "pricing for period is not the latest")

        # create a subscription for the user using the active prices and periods
        subscription = Subscription.objects.create(
            user=user, dinner=True, lunch=True, breakfast=True)

        # calculate the days this subscription is for
        diff = (self.end_date - datetime.date.today()).days
        timedelta = subscription.get_days().days

        # check if both days are equal
        self.assertEqual(
            diff, timedelta, "the different from the current date and the timedelta compared to the value returned by get_days() does not match")

        # manually calculate the prices
        dinner_price = subscription.period.prices.dinner
        lunch_price = subscription.period.prices.lunch
        breakfast_price = subscription.period.prices.breakfast

        payment = subscription.get_total_payment()
        should_be = (dinner_price * timedelta) + (lunch_price *
                                                  timedelta) + (breakfast_price * timedelta)

        self.assertEqual(payment, should_be, "the total prices do not match")

        breakdown = subscription.get_total_payment(detail=True)
        dinner_price_bool = (
            dinner_price * timedelta) == breakdown["charge_for_dinner"]
        lunch_price_bool = (
            lunch_price * timedelta) == breakdown["charge_for_lunch"]
        breakfast_price_bool = (
            breakfast_price * timedelta) == breakdown["charge_for_breakfast"]

        self.assertTrue(
            dinner_price_bool, "dinner price in the breakdown is not equal to the dinner price calculated manually")
        self.assertTrue(
            lunch_price_bool, "lunch price in the breakdown is not equal to the lunch price calculated manually")
        self.assertTrue(breakfast_price_bool,
                        "breakfast price in the breakdown is not equal to the breakfast price calculated manually")

        # terminate the subscription after 10 days
        subscription.terminate()
        self.assertFalse(subscription.is_active)
        self.assertWarns(UserWarning, subscription.terminate)
        # calculate the days this subscription was for
        diff = (subscription.terminated_at - datetime.date.today()).days
        timedelta = subscription.get_days().days

        # check if both days are equal
        self.assertEqual(
            diff, timedelta, "the different from the current date and the timedelta compared to the value returned by get_days() does not match for subscriptions that are terminated")

        # manually calculate the prices
        dinner_price = subscription.period.prices.dinner
        lunch_price = subscription.period.prices.lunch
        breakfast_price = subscription.period.prices.breakfast

        payment = subscription.get_total_payment()
        should_be = (dinner_price * timedelta) + (lunch_price *
                                                  timedelta) + (breakfast_price * timedelta)

        self.assertEqual(payment, should_be, "the total prices do not match")

        breakdown = subscription.get_total_payment(detail=True)
        dinner_price_bool = (
            dinner_price * timedelta) == breakdown["charge_for_dinner"]
        lunch_price_bool = (
            lunch_price * timedelta) == breakdown["charge_for_lunch"]
        breakfast_price_bool = (
            breakfast_price * timedelta) == breakdown["charge_for_breakfast"]

        self.assertTrue(
            dinner_price_bool, "dinner price in the breakdown is not equal to the dinner price calculated manually")
        self.assertTrue(
            lunch_price_bool, "lunch price in the breakdown is not equal to the lunch price calculated manually")
        self.assertTrue(breakfast_price_bool,
                        "breakfast price in the breakdown is not equal to the breakfast price calculated manually")

    def test_multiple_subscriptions(self):
        period = Period.objects.get(is_active=True)
        user = self.User.objects.get(email="student@khi.iba.edu.pk")

        Subscription.objects.create(
            user=user, period=period, dinner=True, lunch=True, breakfast=True)
        Subscription.objects.create(
            user=user, period=period, dinner=True, lunch=True, breakfast=True)

        subscriptions = Subscription.objects.filter(user=user, is_active=True)
        self.assertTrue(subscriptions.count() == 1,
                        "There are more than one active Subscriptions.")
