from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Transaction
from .forms import TransactionForm
import json

@login_required
def dashboard(request):
    # Get last 10 transactions for logged-in user
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:10]
    
    # Calculate total income - using 'type' not 'transaction_type'
    total_income = Transaction.objects.filter(
        user=request.user, 
        type='income'
    ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Calculate total expenses - using 'type' not 'transaction_type'
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

@login_required
def reports(request):
    # Get all user transactions
    transactions = Transaction.objects.filter(user=request.user)
    
    # Apply date filters from GET parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    
    # Calculate totals
    total_income = transactions.filter(type='income').aggregate(total=models.Sum('amount'))['total'] or 0
    total_expenses = transactions.filter(type='expense').aggregate(total=models.Sum('amount'))['total'] or 0
    
    # Get expenses by category
    expenses_by_category = transactions.filter(type='expense').values('category').annotate(
        total=models.Sum('amount')
    ).order_by('-total')
    
    # Convert category IDs to names for JSON
    category_names = {
        '1': 'Food', '2': 'Transport', '3': 'Bills',
        '4': 'Shopping', '5': 'Entertainment', '6': 'Salary'
    }
    
    expenses_list = []
    for item in expenses_by_category:
        cat_id = str(item['category'])
        expenses_list.append({
            'name': category_names.get(cat_id, 'Other'),
            'total': float(item['total'])
        })
    
    # Get monthly summary
    monthly_summary = transactions.filter(type='expense').annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=models.Sum('amount')
    ).order_by('-month')[:6]
    
    # Calculate average expense
    transaction_count = transactions.filter(type='expense').count()
    avg_expense = total_expenses / transaction_count if transaction_count > 0 else 0
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': total_income - total_expenses,
        'transaction_count': transactions.count(),
        'expenses_by_category': expenses_by_category,
        'expenses_by_category_json': json.dumps(expenses_list),
        'monthly_summary': monthly_summary,
        'avg_expense': round(avg_expense, 2),
    }
    return render(request, 'transactions/reports.html', context)

def reports_api(request):
    """API endpoint for filtered reports data"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    transactions = Transaction.objects.filter(user=request.user)
    
    # Apply date filters if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    
    # Calculate totals
    total_income = transactions.filter(type='income').aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = transactions.filter(type='expense').aggregate(total=Sum('amount'))['total'] or 0
    
    # Get expenses by category
    expenses_by_category = transactions.filter(type='expense').values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Convert category IDs to names
    category_names = {
        '1': 'Food', '2': 'Transport', '3': 'Bills',
        '4': 'Shopping', '5': 'Entertainment', '6': 'Salary'
    }
    
    expenses_list = []
    for item in expenses_by_category:
        cat_id = str(item['category'])
        expenses_list.append({
            'name': category_names.get(cat_id, 'Other'),
            'total': float(item['total'])
        })
    
    # Get top category
    top_category = expenses_list[0]['name'] if expenses_list else 'None'
    top_percentage = (expenses_list[0]['total'] / total_expenses * 100) if expenses_list and total_expenses > 0 else 0
    
    # Monthly summary
    monthly_summary = transactions.filter(type='expense').annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('-month')[:6]
    
    monthly_list = []
    for item in monthly_summary:
        monthly_list.append({
            'month': item['month'].strftime('%B %Y'),
            'total': float(item['total'])
        })
    
    return JsonResponse({
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'balance': float(total_income - total_expenses),
        'transaction_count': transactions.count(),
        'expenses_by_category': expenses_list,
        'top_category': top_category,
        'top_percentage': round(top_percentage, 1),
        'monthly_summary': monthly_list,
    })