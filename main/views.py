from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import PaymentInfo
from .forms import PaymentInfoForm

import uuid
import json

from yandex_checkout import Configuration, Payment

Configuration.account_id = '661942' # id магазина в яндекс кассе.
Configuration.secret_key = 'test_2JJzpAq12XYX5uQ7kFnYYKddueEG6i4mmfC5GDtULZg'
# заменить тестовый api key на настоящий


def index_page(request):
    if request.method == 'POST':
        form = PaymentInfoForm(request.POST)
        if form.is_valid():
            
            payment = Payment.create({
                    "amount": {
                        "value": form.cleaned_data['money'],
                        "currency": "RUB"
                    },
                    "confirmation": {
                        "type": "redirect",
                        "return_url": settings.ALLOWED_HOSTS[0]
                    },
                    "capture": True,
                    "description": form.cleaned_data['phone']
                }, uuid.uuid4())
            return HttpResponseRedirect(payment.confirmation.confirmation_url)
    else:
        form = PaymentInfoForm()
    return render(request, 'index.html', {'form': form})

@csrf_exempt
def yandex_confirm(request):
    if request.method == 'POST':
        response_json = json.loads(request.body)
        data = response_json['object']
        if data['status'] == 'waiting_for_capture':
            payment_id = response_json['object']['id']
            data = Payment.capture(payment_id)
            model = PaymentInfo()
        elif data['status'] == 'succeeded':
            model = PaymentInfo()
        else: 
            pass
        try:    
            model.payment_id = data['id']
            model.phone = data['description']
            model.money = int(float(data['amount']['value']))
            model.paid = True
            model.save_with_bonus()
            status = 200
        except:
            status = 404
        return HttpResponse(status=status)


