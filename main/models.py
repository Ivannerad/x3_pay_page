from django.db import models

# Create your models here.
class PaymentInfo(models.Model):
    phone = models.CharField('Телефон', max_length=30)
    money = models.PositiveIntegerField('Сумма пополнения')
    date = models.DateTimeField('Дата пополнения', auto_now_add=True)
    paid = models.BooleanField('Оплачено', default=False)
    payment_id = models.CharField('Ид платежа', max_length=255)
    bonus = models.PositiveIntegerField('Сумма бонуса', default=0)
    
    def save_with_bonus(self):
        self.bonus = self.count_bonus(self.money)
        self.save()
        
    def count_bonus(self, money):
        bonus = 0
        if 500 <= money <= 1499:
            bonus = money * 0.05
        elif 1500 <= money <= 3999:
            bonus = money * 0.1
        elif 4000 <= money:
            bonus = money * 0.15
        else:
            pass
        return round(bonus)
            
    def __str__(self):
        return self.phone
        
    class Meta:
        ordering = ['-date',]
