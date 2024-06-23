from celery import shared_task
from user.models import User
from transactions.models import Transaction
from django.db.models import Sum

@shared_task
def calculate_credit_score(aadhar_id):
    try:
        transactions = Transaction.objects.filter(user=aadhar_id)
        credit_sum = transactions.filter(type='CREDIT').aggregate(credit_sum=Sum('amount'))['credit_sum'] or 0
        debit_sum = transactions.filter(type='DEBIT').aggregate(debit_sum=Sum('amount'))['debit_sum'] or 0
        sum = credit_sum - debit_sum
        credit_score = 300
        if sum>=1000000:
            credit_score = 900
        elif sum<10000:
            credit_score = 300
        else:
            credit_score += int((sum-10000)/1500)
            credit_score = min(credit_score, 900)
        user = User.objects.get(aadhar_id=aadhar_id)
        user.credit_score = credit_score
        user.save()
        return "done"
    except Exception as e:
        print(e)
        pass