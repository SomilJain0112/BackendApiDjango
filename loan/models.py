
from django.db import models
from decimal import Decimal, getcontext


class Loan(models.Model):
    unique_user_id = models.IntegerField(unique=True)  # Remove editable=False
    loan_type = models.CharField(max_length=20, default='CREDIT')
    loan_amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    term_period = models.IntegerField()
    disbursement_date = models.DateField()
    minimum_due = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.unique_user_id:
            # Generate a unique ID here or use another logic to assign it
            self.unique_user_id = self.generate_unique_id()

        # Calculate and set the minimum due
        self.minimum_due = self.get_minimum_due()

        super().save(*args, **kwargs)

    def generate_unique_id(self):
        # Implement your logic to generate a unique ID
        # Example: return some_unique_id_generator_function()
        pass

    def get_minimum_due(self):
        # Set precision for Decimal operations
        getcontext().prec = 28

        # Calculate daily APR accrued
        daily_apr = self.interest_rate / Decimal('365')

        # Calculate minimum due
        principal_balance = self.loan_amount
        minimum_due = (principal_balance * Decimal('0.03')) + (daily_apr ) #* principal_balance)

        # Round minimum_due to two decimal places
        minimum_due = minimum_due.quantize(Decimal('0.01'))

        return minimum_due


class Dues(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    date = models.DateField(null=True)
    paid = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    month_number = models.IntegerField()

    @classmethod
    def create_dues(cls, loan_id):
        loan = Loan.objects.get(id=loan_id)
        minimum_due = loan.get_minimum_due()

        for month in range(1, loan.term_period + 1):
            cls.objects.create(
                loan=loan,
                date=loan.disbursement_date + relativedelta(months=month),
                amount=minimum_due,
                month_number=month,
                active=(month == 1)
            )

        return True

    def receive_payment(self, amount):
        loan = self.loan

        if amount >= self.amount:
            excess_payment = amount - self.amount
            self.paid = True
            self.active = False
            self.amount = 0
            self.save()

            next_due = Dues.objects.filter(loan=loan, paid=False, active=False).order_by('month_number').first()
            if next_due:
                next_due.active = True
                next_due.save()

            if excess_payment > 0:
                loan.reduce_principal(excess_payment)

        else:
            self.amount -= amount
            self.save()
