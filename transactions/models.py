from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    PAYMENT_CHOICES = [
        ('Cash', '💵 Cash'),
        ('Card', '💳 Card'),
        ('Bank Transfer', '🏦 Bank Transfer'),
        ('Digital Wallet', '📱 Digital Wallet'),
        ('Loan/Credit', '🏦 Loan/Credit'),
        ('Other', '📝 Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, blank=True, null=True, default='Cash')
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} - {self.amount}"