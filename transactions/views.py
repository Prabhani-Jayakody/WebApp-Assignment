from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Transaction
from .forms import TransactionForm
import json
from datetime import datetime


# ---------------------------
# COMMON CATEGORY HANDLER
# ---------------------------
def build_expenses(transactions):
    categories = {
        '1': 'Food',
        '2': 'Transport',
        '3': 'Bills',
        '4': 'Shopping',
        '5': 'Entertainment',
        '6': 'Salary',
        '7': 'Health',
        '8': 'Rent',
        '9': 'Other'
    }

    raw_data = transactions.filter(type='expense').values('category').annotate(
        total=Sum('amount')
    )

    # initialize ALL categories with 0
    data_map = {name: 0 for name in categories.values()}

    # fill existing values
    for item in raw_data:
        cat_name = categories.get(str(item['category']), 'Other')
        data_map[cat_name] += float(item['total'])

    return [{"name": k, "total": v} for k, v in data_map.items()]


# ---------------------------
# DASHBOARD
# ---------------------------
@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:10]

    total_income = Transaction.objects.filter(
        user=request.user,
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_expenses = Transaction.objects.filter(
        user=request.user,
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or 0

    balance = total_income - total_expenses

    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
    }
    return render(request, 'transactions/dashboard.html', context)


# ---------------------------
# ADD TRANSACTION (UPDATED WITH CONTEXT DATA)
# ---------------------------
@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            t = form.save(commit=False)
            t.user = request.user
            t.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransactionForm()
    
    # Get recent transactions for sidebar
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Get monthly totals
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_income = Transaction.objects.filter(
        user=request.user,
        type='income',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    monthly_expenses = Transaction.objects.filter(
        user=request.user,
        type='expense',
        date__month=current_month,
        date__year=current_year
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    monthly_balance = monthly_income - monthly_expenses
    
    # Calculate expense percentage
    expense_percentage = round((monthly_expenses / monthly_income * 100) if monthly_income > 0 else 0, 1)
    
    # Check for high expenses warning (超过70%)
    high_expense_warning = expense_percentage > 70
    
    context = {
        'form': form,
        'recent_transactions': recent_transactions,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_balance': monthly_balance,
        'expense_percentage': expense_percentage,
        'high_expense_warning': high_expense_warning,
    }
    return render(request, 'transactions/add_transaction.html', context)


# ---------------------------
# LIST
# ---------------------------
@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    return render(request, 'transactions/list.html', {'transactions': transactions})


# ---------------------------
# EDIT
# ---------------------------
@login_required
def edit_transaction(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    form = TransactionForm(request.POST or None, instance=t)
    if form.is_valid():
        form.save()
        messages.success(request, 'Transaction updated successfully!')
        return redirect('transaction_list')
    return render(request, 'transactions/add_transaction.html', {'form': form})


# ---------------------------
# DELETE
# ---------------------------
@login_required
def delete_transaction(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        t.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')
    return render(request, 'transactions/confirm_delete.html', {'transaction': t})


# ---------------------------
# REPORTS (FIXED VERSION)
# ---------------------------
@login_required
def reports(request):
    transactions = Transaction.objects.filter(user=request.user)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    total_income = transactions.filter(type='income').aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_expenses = transactions.filter(type='expense').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # FIXED CATEGORY HANDLING
    expenses_list = build_expenses(transactions)

    # monthly summary
    monthly_summary = transactions.filter(type='expense').annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('-month')[:6]

    transaction_count = transactions.filter(type='expense').count()
    avg_expense = total_expenses / transaction_count if transaction_count > 0 else 0

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': total_income - total_expenses,
        'transaction_count': transactions.count(),
        'expenses_by_category_json': json.dumps(expenses_list),
        'monthly_summary': monthly_summary,
        'avg_expense': round(avg_expense, 2),
    }

    return render(request, 'transactions/reports.html', context)


# ---------------------------
# API (FIXED VERSION)
# ---------------------------
def reports_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Not authenticated'}, status=401)

    transactions = Transaction.objects.filter(user=request.user)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)

    total_income = transactions.filter(type='income').aggregate(
        total=Sum('amount')
    )['total'] or 0

    total_expenses = transactions.filter(type='expense').aggregate(
        total=Sum('amount')
    )['total'] or 0

    expenses_list = build_expenses(transactions)

    top_category = max(expenses_list, key=lambda x: x['total'])['name'] if expenses_list else 'None'
    top_percentage = (
        (max(expenses_list, key=lambda x: x['total'])['total'] / total_expenses * 100)
        if expenses_list and total_expenses > 0 else 0
    )

    monthly_summary = transactions.filter(type='expense').annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('-month')[:6]

    monthly_list = [
        {
            'month': item['month'].strftime('%B %Y'),
            'total': float(item['total'])
        }
        for item in monthly_summary
    ]

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