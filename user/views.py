from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from user.models import User
from user.tasks import calculate_credit_score

@csrf_exempt
def create_user(request):
    try:
        if request.method == 'POST':
            data = request.POST  
            new_user = User.objects.create(
                        name=data['name'],
                        email=data['email'],
                        annual_income=data['annual_income'],
                        aadhar_id=data['aadhar_id'],
                    )
            calculate_credit_score.apply_async([data['aadhar_id']])
            return JsonResponse({'unique_user_id': new_user.pk}, status=201)
        else:
            return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

# Create your views here.
