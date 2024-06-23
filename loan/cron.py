from loan.models import Dues
from datetime import datetime

def check_dues():
    today_date = datetime.date()
    Dues.objects.filter(date=today_date).update(active=True)
