from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from .models import Transaction
from .forms import TransactionForm

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