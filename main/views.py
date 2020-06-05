from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import PaymentInfo
from .forms import PaymentInfoForm
from .reservation import *

import uuid
import json
import re

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
                    "receipt": {
                         "customer": {
                            "full_name": "ФИО",
                            "phone": ''.join(re.findall(r'\d', form.cleaned_data['phone']))
                                     },
                        "items": [{
                            "description": "Оплата бронирования",
                            "quantity": "1.00",
                            "amount": {
                                "value": form.cleaned_data['money'],
                                "currency": "RUB"
                                        },
                            "vat_code": "2",
                            "payment_mode": "full_prepayment",
                            "payment_subject": "commodity"}]
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
            # если платеж ожидает подтверждения, подтверждаю
            model = PaymentInfo()
        elif data['status'] == 'succeeded':
            model = PaymentInfo()
        else: 
            pass
        try:    
            model.payment_id = data['id']
            # id платежа из яндекс кассы
            model.phone = '+' + ''.join(re.findall(r'\d', data['description']))
            # привожу + 7 (900) 00-000-00 к +79000000000
            model.money = int(float(data['amount']['value']))
            # привожу строку 100.00 к цыфре 100
            model.paid = True
            model.save_with_bonus()
            mount = str(model.money + model.count_bonus(model.money))
            # Привожу сумму + бонус к строке для передачи в апи 
            continue_play(model.phone, mount, 1) # last argument it's time in hours
            status = 200
        except:
            status = 200
        return HttpResponse(status=status)


