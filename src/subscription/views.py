from django.shortcuts import render

from django.http import HttpResponse


from .models import Subscription


def index(request):
    return render(request, 'dashboard.html', {})


def all_subscriptions(request):
    # print(dir(request))
    subs = Subscription.objects.all()
    context = {
        'subs': subs
    }
    return render(request, 'subscriptions.html', context)



def single_subscription(request, id):
    sub = Subscription.objects.get(id=id)
    context = {
        'sub': sub
    }
    return render(request, 'single-sub.html', context)