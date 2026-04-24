from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from .models import Transaction, Category
from .forms import TransactionForm
import json
from datetime import datetime, timedelta


# Helper function for category mapping using actual Category model
def build_expenses(transactions):
    raw_data = transactions.filter(type='expense').values('category__name').annotate(
        total=Sum('amount')
    )
    
    # Initialize with 0 for all categories
    all_categories = Category.objects.all()
    data_map = {cat.name: 0 for cat in all_categories}
    
    # Fill existing values
    for item in raw_data:
        cat_name = item['category__name']
        if cat_name:
            data_map[cat_name] += float(item['total'])
    
    return [{"name": k, "total": v} for k, v in data_map.items() if v > 0]


# ---------------------------
# DASHBOARD
# ---------------------------
@login_required
def dashboard(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    total_income = float(Transaction.objects.filter(user=request.user, type='income').aggregate(Sum('amount'))['amount__sum'] or 0)
    total_expenses = float(Transaction.objects.filter(user=request.user, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)
    balance = total_income - total_expenses
    savings_rate = round((balance / total_income * 100), 1) if total_income > 0 else 0
    
    # Get all categories for mapping
    all_categories = Category.objects.all()
    category_names_dict = {cat.id: cat.name for cat in all_categories}
    
    # Expense chart data - Show category names from actual Category model
    expense_data = Transaction.objects.filter(
        user=request.user, 
        type='expense'
    ).values('category').annotate(total=Sum('amount')).order_by('-total')[:6]
    
    category_labels = []
    category_values = []
    for item in expense_data:
        if item['category']:
            cat_name = category_names_dict.get(item['category'], 'Other')
            category_labels.append(cat_name)
            category_values.append(float(item['total']))
    
    # Top category insight
    top_cat = Transaction.objects.filter(
        user=request.user, 
        type='expense'
    ).values('category').annotate(total=Sum('amount')).order_by('-total').first()
    
    if top_cat and top_cat['category']:
        cat_id = top_cat['category']
        top_category = category_names_dict.get(cat_id, 'Other')
        top_percentage = round((float(top_cat['total']) / total_expenses * 100), 1) if total_expenses > 0 else 0
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
    monthly_expenses = float(Transaction.objects.filter(user=request.user, type='expense', date__gte=first_day).aggregate(Sum('amount'))['amount__sum'] or 0)
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
        
        income = float(Transaction.objects.filter(
            user=request.user, type='income', 
            date__year=target_year, date__month=target_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0)
        
        expense = float(Transaction.objects.filter(
            user=request.user, type='expense', 
            date__year=target_year, date__month=target_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0)
        
        income_data.append(income)
        expense_data_list.append(expense)
    
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
            # Ensure payment_method is saved
            if 'payment_method' in request.POST:
                t.payment_method = request.POST.get('payment_method')
            t.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TransactionForm()
    
    recent = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    today = datetime.now()
    monthly_income = float(Transaction.objects.filter(user=request.user, type='income', date__month=today.month, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0)
    monthly_expenses = float(Transaction.objects.filter(user=request.user, type='expense', date__month=today.month, date__year=today.year).aggregate(Sum('amount'))['amount__sum'] or 0)
    
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
# REPORTS (UPDATED)
# ---------------------------
@login_required
def reports(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to current month if no filter
    today = datetime.now().date()
    if not start_date:
        start_date = today.replace(day=1)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = today
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    filtered = transactions.filter(date__gte=start_date, date__lte=end_date)
    
    # Previous period for comparison
    days_diff = (end_date - start_date).days
    prev_end_date = start_date - timedelta(days=1)
    prev_start_date = prev_end_date - timedelta(days=days_diff)
    
    prev_filtered = transactions.filter(date__gte=prev_start_date, date__lte=prev_end_date)
    
    # Current period stats
    total_income = float(filtered.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0)
    total_expenses = float(filtered.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)
    net_savings = total_income - total_expenses
    savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
    transaction_count = filtered.count()
    
    # Daily average
    days_in_period = (end_date - start_date).days + 1
    avg_daily_expense = total_expenses / days_in_period if days_in_period > 0 else 0
    avg_transaction = total_expenses / transaction_count if transaction_count > 0 else 0
    
    # Previous period stats
    prev_income = float(prev_filtered.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0)
    prev_expenses = float(prev_filtered.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)
    prev_savings = prev_income - prev_expenses
    
    vs_previous_income = ((total_income - prev_income) / prev_income * 100) if prev_income > 0 else 0
    vs_previous_expense = ((total_expenses - prev_expenses) / prev_expenses * 100) if prev_expenses > 0 else 0
    vs_previous_savings = ((net_savings - prev_savings) / prev_savings * 100) if prev_savings > 0 else 0
    
    # Category data for chart
    category_expenses = filtered.filter(type='expense').values('category__name').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    category_names = []
    category_values = []
    category_details = []
    
    icons = {
        'Food': '🍔', 'Transport': '🚗', 'Bills': '💡', 'Shopping': '🛍️', 
        'Health': '🏥', 'Entertainment': '🎬', 'Rent': '🏠', 'Salary': '💰', 
        'Other Income': '💵', 'Freelance': '💻', 'Investment': '📈',
        'Gift': '🎁', 'Education': '📚', 'Insurance': '🛡️', 'Other': '📌'
    }
    
    colors = ['#34D399', '#F59E0B', '#F87171', '#3B82F6', '#8B5CF6', '#EC4899', '#06B6D4', '#84CC16']
    
    for idx, item in enumerate(category_expenses):
        cat_name = item['category__name'] or 'Other'
        total_amount = float(item['total'])
        percentage = (total_amount / total_expenses * 100) if total_expenses > 0 else 0
        category_names.append(cat_name)
        category_values.append(total_amount)
        category_details.append({
            'name': cat_name,
            'icon': icons.get(cat_name, '📌'),
            'amount': total_amount,
            'percentage': round(percentage, 1),
            'color': colors[idx % len(colors)]
        })
    
    # Payment method data - FIXED to show all payment methods
    payment_expenses = filtered.filter(type='expense').values('payment_method').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    payment_names = []
    payment_values = []
    payment_details = []
    
    payment_icons = {
        'Cash': '💵',
        'Card': '💳',
        'Bank Transfer': '🏦',
        'Digital Wallet': '📱',
        'Loan/Credit': '🏦',
        'Other': '📝'
    }
    
    for item in payment_expenses:
        method = item['payment_method'] or 'Not Specified'
        total_amount = float(item['total'])
        payment_names.append(method)
        payment_values.append(total_amount)
        payment_details.append({
            'name': method,
            'icon': payment_icons.get(method, '📌'),
            'percentage': round((total_amount / total_expenses * 100), 1) if total_expenses > 0 else 0,
            'amount': total_amount
        })
    
    # Monthly trend data
    months = []
    monthly_income = []
    monthly_expenses_list = []
    
    for i in range(5, -1, -1):
        target_month = today.month - i
        target_year = today.year
        
        if target_month <= 0:
            target_month += 12
            target_year -= 1
        
        month_date = datetime(target_year, target_month, 1)
        months.append(month_date.strftime('%b %Y'))
        
        income = float(filtered.filter(
            type='income', 
            date__year=target_year, 
            date__month=target_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0)
        
        expense = float(filtered.filter(
            type='expense', 
            date__year=target_year, 
            date__month=target_month
        ).aggregate(Sum('amount'))['amount__sum'] or 0)
        
        monthly_income.append(income)
        monthly_expenses_list.append(expense)
    
    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
        'savings_rate': savings_rate,
        'transaction_count': transaction_count,
        'avg_daily_expense': avg_daily_expense,
        'avg_transaction': avg_transaction,
        'vs_previous_income': vs_previous_income,
        'vs_previous_expense': vs_previous_expense,
        'vs_previous_savings': vs_previous_savings,
        'category_data': json.dumps({
            'labels': category_names,
            'values': category_values,
            'details': category_details
        }),
        'payment_data': json.dumps({
            'labels': payment_names,
            'values': payment_values,
            'details': payment_details
        }),
        'monthly_chart_data': json.dumps({
            'labels': months,
            'income': monthly_income,
            'expenses': monthly_expenses_list
        }),
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
    
    total_income = float(transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0)
    total_expenses = float(transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0)
    expenses_list = build_expenses(transactions)
    
    return JsonResponse({
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': total_income - total_expenses,
        'transaction_count': transactions.count(),
        'expenses_by_category': expenses_list,
        'top_category': max(expenses_list, key=lambda x: x['total'])['name'] if expenses_list else 'None',
        'top_percentage': round((max(expenses_list, key=lambda x: x['total'])['total'] / total_expenses * 100), 1) if expenses_list and total_expenses > 0 else 0,
    })