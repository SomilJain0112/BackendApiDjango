from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class Transaction(models.Model):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'
    TYPE_CHOICES = [
        (DEBIT, 'Debit'),
        (CREDIT, 'Credit'),
    ]

    user = models.CharField(max_length=100)
    date = models.DateField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.IntegerField()
    
    
    
    
    
               
    
    

    def clean(self):
        super().clean()
        if self.type not in ['DEBIT', 'CREDIT']:
            raise ValidationError('The value of type must be either "DEBIT" or "CREDIT"')


class Billing(models.Model):
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'
    
    user = models.CharField(max_length=100)
    billing_date = models.DateField()
    due_date = models.DateField()
    min_due = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.05)  # 5% annual interest rate
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    past_due_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def calculate_daily_interest(self):
        daily_interest_rate = self.interest_rate / 365
        return self.balance * daily_interest_rate

    def accrue_interest(self):
        today = timezone.now().date()
        days = (today - self.billing_date).days
        for _ in range(days):
            self.balance += self.calculate_daily_interest()
            self.billing_date += timedelta(days=1)
        self.update_min_due()  # Update minimum due after accruing interest
        self.save()

    def update_min_due(self):
        daily_interest = self.calculate_daily_interest()
        days_in_month = (self.due_date - self.billing_date).days
        self.min_due = daily_interest * days_in_month
        self.save()

    def check_past_due(self):
        today = timezone.now().date()
        if today > self.due_date and self.balance > 0:
            self.past_due_amount += self.min_due
            self.save()

    def remind_to_pay(self):
        if self.past_due_amount > 0:
            return f"Reminder: Your past due amount is ${self.past_due_amount}. Please settle this amount first."
        return "No past due amount to pay."

    def make_payment(self, amount):
        # First, pay off past due amount if any
        if self.past_due_amount > 0:
            if amount >= self.past_due_amount:
                amount -= self.past_due_amount
                self.past_due_amount = 0
            else:
                self.past_due_amount -= amount
                amount = 0
        
        # Then, pay off current minimum due if any
        if amount > 0:
            if amount >= self.min_due:
                amount -= self.min_due
                self.min_due = 0
            else:
                self.min_due -= amount
                amount = 0
        
        if amount > 0:
            print(f"Remaining amount of ${amount} exceeds all outstanding dues. Consider refunding.")
        else:
            print("Payment successfully processed.")

    def save(self, *args, **kwargs):
        # Set the due date 15 days after the billing date if not set explicitly
        if self.due_date:
            self.due_date = self.billing_date + timedelta(days=15)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Billing for {self.user} on {self.billing_date}"