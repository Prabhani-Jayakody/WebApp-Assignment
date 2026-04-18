from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Transaction
from .forms import TransactionForm
from django.db.models.functions import TruncMonth

@login_required
def dashboard(request):
    # Get last 10 transactions for logged-in user
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:10]
    
    # Calculate total income - NOTE: using 'type' not 'transaction_type'
    total_income = Transaction.objects.filter(
        user=request.user, 
        type='income'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Calculate total expenses - NOTE: using 'type' not 'transaction_type'
    total_expenses = Transaction.objects.filter(
        user=request.user, 
        type='expense'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Calculate balance
    balance = total_income - total_expenses
    
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
    }
    return render(request, 'transactions/dashboard.html', context)

@login_required
def reports(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    total_income = transactions.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or 0
    total_expenses = transactions.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
    
    expenses_by_category = transactions.filter(type='expense').values('category').annotate(
        total=models.Sum('amount')
    ).order_by('-total')
    category_names = {
        '1': 'Food',
        '2': 'Transport', 
        '3': 'Bills',
        '4': 'Shopping',
        '5': 'Entertainment',
        '6': 'Salary',
        '7': 'Other',
    }
    
    for item in expenses_by_category:
        item['category_name'] = category_names.get(str(item['category']), item['category'])

    monthly_summary = transactions.filter(
        type='expense'
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=models.Sum('amount')
    ).order_by('-month')[:6]
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': total_income - total_expenses,
        'expenses_by_category': expenses_by_category,
        'category_names': category_names,
        'monthly_summary': monthly_summary,
        'transaction_count': transactions.count(),
    }
    return render(request, 'transactions/reports.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            return redirect('transaction_list')
    else:
        form = TransactionForm()
    return render(request, 'transactions/add_transaction.html', {'form': form})

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions/list.html', {'transactions': transactions})

@login_required
def edit_transaction(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    form = TransactionForm(request.POST or None, instance=t)
    if form.is_valid():
        form.save()
        return redirect('transaction_list')
    return render(request, 'transactions/add_transaction.html', {'form': form})

@login_required
def delete_transaction(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        t.delete()
        return redirect('transaction_list')
    return render(request, 'transactions/confirm_delete.html', {'transaction': t})