## Types of users
------------------------------------------------------------
* **Student** that is just there for subscriptions 
    * erp required
    * email required only ending with `iba.edu.pk`

* **Admin** just to view and handle the users and the website
    * email required but does not have to end with `iba.edu.pk`
    * erp is not required and will be set as "0"

* **Not admin Not Student User** 
    * email is required does not have to end with `iba.edu.pk`
    * erp is not required and will be set as 0

* **Student Admins** there to handle mess operations and finances
    * email required only ending with `iba.edu.pk`
    * erp required



## Models
------------------------------------------------------------
### accounts
- [Wallet](#wallet)
- [MessAccount](#messaccount)
- [Revenue](#revenue)
- [Inventory](#inventory)
- [Price](#price)

### subscription
- [Period](#period)
- [Subscription](#subscription)

### users
- [User](#user)

<br/>

### Details:

#### Wallet
- `credit(*args,**kwargs)`(model method) : subtracts money from the Wallet
- `debit(*args,**kwargs)` (model method) : adds money to the wallet

**Disclaimer:** the methods on wallet are not meant to be used directly only add money to wallets through the __MessAccount__ model

#### MessAccount
- `topup_wallet(*args,**kwargs)`(manager method): see [example](#example-wallet)
- `add_inventory(*args,**kwargs)`(manager method): see [example](#example-inventory)

#### Revenue
`null`

#### Inventory
`null` for now use the mess account method

#### Price 
simply create using example:
```python
price = Price.objects.create(
            dinner=210,
            lunch=200,
            breakfast=180,
            surcharge=500
        )
```

#### Period
```python
# creating a date instance from the datetime.date class
end_date = datetime.date(2023, 3, 14)
# passing it to the period
period = Period.objects.create(end_date=end_date)
```
**Note:** make sure you have an active pricing before calling create

#### Subscription
use `user.subscribe()` to interact with this model see [example](#example-subscription)

#### User
see [detail](#types-of-users)
- `create_user()`
- `create_superuser()`

## Flow of money
------------------------------------------------------------

* adding money to the wallet will also add money to mess account.
    <p>
    Model <strong>MessAccount</strong> has a method in its manager called <strong>topup_wallet</strong>.
    Using this method a wallet can be topped up by passing user it and the amount
    </p>

    ### Example Wallet

    ```python
    # getting a user of your choice
    user = User.objects.get(email="normaluser@khi.iba.edu.pk")

    # adding money to the users wallet
    MessAccount.objects.topup_wallet(amount = 10000, user = user)
    ```
    __**NOTE:** Wallet has methods credit and debit on it but they are not to be used just yet. They will be used for adjustments in the next phase__

* Buying inventory would reduce the mess account but it would increase the inventory.
    <p>
        Model <strong>MessAccount</strong> has a method in its manager called <strong>add_inventory</strong>.
        Using this method inventory can be bought.
    </p>

    ### Example Inventory

    ```python
    # ideal usecase
    MessAccount.objects.add_inventory(
            "Chicken",
            23,
            "KG",
            20000
        )
    
    # will throw an error
    MessAccount.objects.add_inventory(
            "Chicken",
            23,
            "kilo",
            20000
        )
    ```
* each user can be subscribed to the currently active period by calling the user.subscribe() method by passing in the times the user wants to avail the services.
    ### Example Subscription
    ```python
    # get a user instance
    user = User.objects.get(email="normaluser@khi.iba.edu.pk")

    # subscribe the user to a specific service
    user.subscribe(dinner=True,breakfast=True)
    ```
    __**NOTE:** please make sure that pricing and period are set before using this method. Subscription needs an active period and pricing__
    
    Follow the order Below

        1) create Pricing
        2) create Period
        3) create Subscription


## Cases Handled
------------------------------------------------------------
* wallet top ups increase the mess account and log the appropriate action
* Wallet top up shows the complete flow of cash from a to. 
* buying inventory reduces the mess account. 
* creating a new pricing will automatically deactivate the last active pricing. Hence at any point in time there is at least one or zero active pricing
*  creating a new period will automatically deactivate the last active period. Hence at any point in time there is at least one or zero active pricing
* creating a subscription will automatically assign it into the appropriate period and subsequently the appropriate pricing. 
* there will be a check for stale billing period i.e you are trying to subscribe to a billing period that has ended but was not marked inactive. an Error will be thrown in that case. This can happen when:
    * The user forgot to create a new period and tries to subscribe a student.