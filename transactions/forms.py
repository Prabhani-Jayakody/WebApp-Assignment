from django import forms
from .models import Transaction, Category

class TransactionForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('Cash', '💵 Cash'),
        ('Card', '💳 Card'),
        ('Bank Transfer', '🏦 Bank Transfer'),
        ('Digital Wallet', '📱 Digital Wallet'),
        ('Loan/Credit', '🏦 Loan/Credit'),
        ('Other', '📝 Other'),
    ]
    
    TYPE_CHOICES = [
        ('income', '💰 Income'),
        ('expense', '💸 Expense'),
    ]
    
    type = forms.ChoiceField(choices=TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label="Select a category", widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = Transaction
        fields = ['type', 'amount', 'category', 'payment_method', 'description', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={
                'min': '0.01',
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control', 
                'placeholder': 'Enter description (e.g., Bought groceries, Paid electricity bill...)'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field.widget.__class__.__name__ != 'CheckboxInput':
                if field.widget.attrs.get('class'):
                    field.widget.attrs['class'] += ' form-control'
                else:
                    field.widget.attrs['class'] = 'form-control'
        
        # Custom placeholder for amount
        self.fields['amount'].widget.attrs['placeholder'] = '0.00'
        
        # Help text for fields
        self.fields['description'].help_text = "Add details to remember this transaction"
        self.fields['payment_method'].help_text = "How did you pay for this?"

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount
    
    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('type')
        payment_method = cleaned_data.get('payment_method')
        
        # For expense transactions, default to Cash if not specified
        if transaction_type == 'expense' and not payment_method:
            cleaned_data['payment_method'] = 'Cash'
        
        return cleaned_data