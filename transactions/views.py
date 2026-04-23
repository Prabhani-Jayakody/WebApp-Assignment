from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from .models import Transaction
from .forms import TransactionForm
import json
from datetime import datetime


# Helper function for category mapping
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
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    total_income = Transaction.objects.filter(user=request.user, type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = Transaction.objects.filter(user=request.user, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = total_income - total_expenses
    savings_rate = round((balance / total_income * 100), 1) if total_income > 0 else 0
    
    # Category mapping
    category_names = {
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
    
    # Expense chart data - Show category names
    expense_data = Transaction.objects.filter(
        user=request.user, 
        type='expense'
    ).values('category').annotate(total=Sum('amount')).order_by('-total')[:6]
    
    category_labels = []
    category_values = []
    for item in expense_data:
        cat_id = str(item['category'])
        cat_name = category_names.get(cat_id, 'Other')
        category_labels.append(cat_name)
        category_values.append(float(item['total']))
    
    # Top category insight
    top_cat = Transaction.objects.filter(
        user=request.user, 
        type='expense'
    ).values('category').annotate(total=Sum('amount')).order_by('-total').first()
    
    if top_cat:
        cat_id = str(top_cat['category'])
        top_category = category_names.get(cat_id, 'Other')
        top_percentage = round((top_cat['total'] / total_expenses * 100), 1) if total_expenses > 0 else 0
    else:
        top_category = 'None'
        top_percentage = 0
    
    # Daily average
    today = datetime.now()
    first_day = today.replace(day=1)
    if today.month == 12:
        next_month = today.replace(year=today.year+1, month=1, day=1)
    else:
        next_month = today.replace(month=today.month+1, day=1)
    days_in_month = (next_month - first_day).days
    monthly_expenses = Transaction.objects.filter(user=request.user, type='expense', date__gte=first_day).aggregate(Sum('amount'))['amount__sum'] or 0
    avg_daily = round(monthly_expenses / days_in_month, 2) if days_in_month > 0 else 0
    
    # Monthly comparison (last 6 months)
    months = []
    income_data = []
    expense_data_list = []
    
    for i in range(5, -1, -1):
        target_month = today.month - i
        target_year = today.year
        
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        
        month_date = datetime(target_year, target_month, 1)
        months.append(month_date.strftime('%b %Y'))
        
        income = Transaction.objects.filter(
            user=request.user, type='income', 
            date__year=target_year, date__month=target_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        expense = Transaction.objects.filter(
            user=request.user, type='expense', 
            date__year=target_year, date__month=target_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        income_data.append(float(income))
        expense_data_list.append(float(expense))
    
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'savings_rate': savings_rate,
        'transaction_count': Transaction.objects.filter(user=request.user).count(),
        'category_labels': json.dumps(category_labels),
        'category_values': json.dumps(category_values),
        'month_labels': json.dumps(months),
        'monthly_income_data': json.dumps(income_data),
        'monthly_expense_data': json.dumps(expense_data_list),
        'top_category': top_category,
        'top_percentage': top_percentage,
        'avg_daily_expense': avg_daily,
    }
    return render(request, 'transactions/dashboard.html', context)


# ---------------------------
# ADD TRANSACTION
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
    
    recent = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    today = datetime.now()
    monthly_income = Transaction.objects.filter(user=request.user, type='income', date__month=today.month, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_expenses = Transaction.objects.filter(user=request.user, type='expense', date__month=today.month, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'form': form,
        'recent_transactions': recent,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'monthly_balance': monthly_income - monthly_expenses,
        'expense_percentage': round((monthly_expenses / monthly_income * 100), 1) if monthly_income > 0 else 0,
        'high_expense_warning': (monthly_expenses / monthly_income * 100) > 70 if monthly_income > 0 else False,
    }
    return render(request, 'transactions/add_transaction.html', context)


# ---------------------------
# LIST, EDIT, DELETE
# ---------------------------
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
        messages.success(request, 'Transaction updated!')
        return redirect('transaction_list')
    return render(request, 'transactions/add_transaction.html', {'form': form})

@login_required
def delete_transaction(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        t.delete()
        messages.success(request, 'Transaction deleted!')
        return redirect('transaction_list')
    return render(request, 'transactions/confirm_delete.html', {'transaction': t})


# ---------------------------
# REPORTS & API
# ---------------------------
@login_required
def reports(request):
    transactions = Transaction.objects.filter(user=request.user)
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    if start: transactions = transactions.filter(date__gte=start)
    if end: transactions = transactions.filter(date__lte=end)
    
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    monthly_summary = transactions.filter(type='expense').annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('-month')[:6]
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': total_income - total_expenses,
        'transaction_count': transactions.count(),
        'expenses_by_category_json': json.dumps(build_expenses(transactions)),
        'monthly_summary': monthly_summary,
        'avg_expense': round(total_expenses / transactions.filter(type='expense').count(), 2) if transactions.filter(type='expense').count() > 0 else 0,
    }
    return render(request, 'transactions/reports.html', context)

def reports_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    transactions = Transaction.objects.filter(user=request.user)
    start = request.GET.get('start_date')
    end = request.GET.get('end_date')
    if start: transactions = transactions.filter(date__gte=start)
    if end: transactions = transactions.filter(date__lte=end)
    
    total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expenses = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    expenses_list = build_expenses(transactions)
    
    return JsonResponse({
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'balance': float(total_income - total_expenses),
        'transaction_count': transactions.count(),
        'expenses_by_category': expenses_list,
        'top_category': max(expenses_list, key=lambda x: x['total'])['name'] if expenses_list else 'None',
        'top_percentage': round((max(expenses_list, key=lambda x: x['total'])['total'] / total_expenses * 100), 1) if expenses_list and total_expenses > 0 else 0,
    })