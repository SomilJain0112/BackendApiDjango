from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from loan.models import Loan, Dues
from user.models import User
from dateutil.relativedelta import relativedelta
from datetime import datetime
# Create your views here.

def calculate_emi(loan_amount, interest_rate, term_period):
    r = (interest_rate / 12) / 100  # Convert annual interest rate to monthly and percentage to decimal
    n = term_period
    emi = (loan_amount * r * (1 + r)**n) / ((1 + r)**n - 1)
    return emi

def user_validation(user):
    if user.credit_score<450:
        raise Exception("not enough credit score")
    elif user.annual_income<150000:
        raise Exception("Income criteria failde")
    
def emi_validation(user, loan_amount, interest_rate, term_period):
    emi = calculate_emi(loan_amount, interest_rate, term_period)
    if interest_rate<12:
        raise Exception("Interest Rate should be more than 12")
    elif loan_amount>5000:
        raise Exception("amount too high")
    elif 0.2*int(user.annual_income)<emi:
        raise Exception("annual income too less for the loan")
    elif emi<50:
        raise Exception("interest too low")

@csrf_exempt
def apply_loan(request):
    try:
        if request.method == 'POST':
            data = request.POST
            uuid = data['unique_user_id']
            loan_amount = int(data['loan_amount'])
            interest_rate = int(data['interest_rate'])
            term_period = int(data['term_period'])
            disbursement_date = datetime.strptime(data['date'], "%Y-%m-%d")

            user = User.objects.get(pk = uuid)
            user_validation(user)
            emi_validation(user, loan_amount, interest_rate, term_period)

            emi = calculate_emi(loan_amount, interest_rate, term_period)

            loan = Loan.objects.create(
                unique_user_id = user.pk,
                loan_amount = loan_amount,
                interest_rate = interest_rate,
                term_period = term_period,
                disbursement_date = disbursement_date
            )
            due_dates = []
            curr_date = disbursement_date + relativedelta(months=1)
            for i in range(term_period):
                print(curr_date)
                Dues.objects.create(
                    loan_id = loan.pk,
                    date = curr_date,
                    amount = emi,
                    month_number = i+1
                )
                due_dates.append({
                    'date' : curr_date,
                    'amount_due' : emi
                })
                curr_date = curr_date + relativedelta(months=1)
            
            res = {
                'loan_id' : loan.pk,
                'due_dates' : due_dates
            }

            return JsonResponse(res, status=200)
        else:
            return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@csrf_exempt
def get_statement(request):
    try:
        data = request.POST

        loan_id = data['loan_id']

        loan = Loan.objects.get(pk=loan_id)

        res = {
            'date' : loan.disbursement_date,
            'principal' : loan.loan_amount,
            'interest' : loan.interest_rate,
        }

        dues = Dues.objects.filter(loan_id=loan_id, paid=False).order_by('date')
        due_dates = []
        
        for due in dues:
            due_dates.append({
                'date': due.date,
                'amount_due': due.amount,
            })
        
        res['due_dates'] = due_dates
        return JsonResponse(res, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    
@csrf_exempt
def make_payment(request):
    try:
        if request.method == 'POST':
            data = request.POST
            loan_id = int(data['loan_id'])
            amount = float(data['amount'])

            loan = Loan.objects.get(pk=loan_id)

            unpaid_dues = Dues.objects.filter(loan_id=loan_id, paid=False).order_by('date')
            active_dues = unpaid_dues.filter(loan_id=loan_id, paid=False, active=True).order_by('date')
            if active_dues.count() == 0:
                raise Exception("no dues to be paid")
            if active_dues[0].amount>amount:
                raise Exception("not enougn amount")

            principle = float(loan.loan_amount)

            principle -= (amount - float(active_dues[0].amount))
            principle = max(principle, 0.0)
            principle = principle/loan.term_period * (active_dues.count()-1)

            loan.loan_amount = principle
            loan.save()
            new_emi = calculate_emi(principle, float(loan.interest_rate), active_dues.count()-1)
            print(new_emi, active_dues[0].amount)
            first_due = active_dues[0]
            first_due.paid=True
            first_due.save()

            for i in range(active_dues.count()-1):
                due = active_dues[i+1]
                due.amount = new_emi
                due.save()

            return JsonResponse({'succuess' : True }, status=200)
        else:
            return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
