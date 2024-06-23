from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    annual_income = models.DecimalField(max_digits=15, decimal_places=2)
    aadhar_id = models.CharField(max_length=12, unique=True)
    credit_score = models.IntegerField(default=0)

    def __str__(self):
        return self.name

# Define a signal handler function
@receiver(post_save, sender=User)
def update_credit_score(sender, instance, created, **kwargs):
    if created or instance.pk is None:
        # If the instance is being created or not yet saved to the database
        calculate_and_save_credit_score(instance)
    else:
        # Check if annual_income has changed
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.annual_income != instance.annual_income:
                calculate_and_save_credit_score(instance)
        except User.DoesNotExist:
            pass

def calculate_and_save_credit_score(user):
    # Determine credit score based on annual income
    if user.annual_income >= 1000000:
        user.credit_score = 900
    elif user.annual_income <= 10000:
        user.credit_score = 300
    else:
        # For annual incomes between Rs. 10,000 and Rs. 1,000,000
        # Calculate the difference from Rs. 10,000
        income_difference = user.annual_income - 10000
        # Calculate how many Rs. 15,000 increments fit into the difference
        increment_count = income_difference / 15000
        # Calculate the credit score adjustment
        adjustment = int(increment_count) * 10
        user.credit_score = 300 + adjustment
        
    user.save(update_fields=['credit_score'])
# Assuming you have a Transaction model or similar for storing transactions

    def __str__(self):
        return f"Transaction of {self.user}: {self.credit} - {self.debit}"
