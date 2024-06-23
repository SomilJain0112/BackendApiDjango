from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from transactions.models import Transaction
import os
import csv

def initialise(request):
    try:
        # Adjust the file path separator to use either '/' or '\\'
        csv_file_path = os.path.join(settings.BASE_DIR, 'public', 'static', 'transactions_data_backend__1_.csv') 
        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Assuming 'user', 'date', 'transaction_type', 'amount' are fields in your CSV
                Transaction.objects.create(
                    user=row['user'],
                    date=row['date'],
                    type=row['transaction_type'],  # 'type' is a reserved keyword, consider renaming this field
                    amount=row['amount'],
                )
        return JsonResponse({'status': 'Transactions imported successfully', 'code': 200})
    except FileNotFoundError:
        return JsonResponse({'status': 'CSV file not found', 'code': 404})
    except ValidationError as e:
        return JsonResponse({'status': str(e), 'code': 400})
    except Exception as e:
        return JsonResponse({'status': 'Error importing transactions', 'code': 500})


def generate_billing(user):
    # Get the current billing record or create a new one
    billing, created = Billing.objects.get_or_create(user=user)

    # Accrue interest up to today's date
    billing.accrue_interest()

    # Calculate the minimum due amount
    billing.update_min_due()

    return billing