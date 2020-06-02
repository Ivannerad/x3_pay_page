from django.urls import path
from .views import *

urlpatterns = [
    path('', index_page, name='index_page'),
    path('success_payment', yandex_confirm, name='success_payment'),

]
