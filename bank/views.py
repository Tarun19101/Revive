from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import CashFlow
from .forms import CashFlowForm
from datetime import date, timedelta
from django.http import HttpResponse

@login_required
def bank_home(request):
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_start = date(today.year, today.month, 1)

    # This week's expenses
    expense = CashFlow.objects.filter(
        user=request.user,
        cash_flow_type='expense',
        date__gte=week_ago
    ).order_by('-date')

    # This month's entries
    income = CashFlow.objects.filter(
        user=request.user,
        cash_flow_type='income',
        date__gte=month_start
    ).order_by('-date')

    loan_taken = CashFlow.objects.filter(
        user=request.user,
        cash_flow_type='loan_taken',
        status='pending',
        date__gte=month_start
    ).order_by('-date')

    loan_given = CashFlow.objects.filter(
        user=request.user,
        cash_flow_type='loan_given',
        status='pending',
        date__gte=month_start
    ).order_by('-date')

    form = CashFlowForm()

    if request.method == 'POST':
        form = CashFlowForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            # Auto-clear income/expense, keep loans pending by default
            if entry.cash_flow_type in ['income', 'expense']:
                entry.status = 'cleared'
            entry.save()
            return redirect('bank_home')

    context = {
        'form': form,
        'expense': expense,
        'income': income,
        'loan_taken': loan_taken,
        'loan_given': loan_given,
        'total_money': get_total_money(request.user),
        'monthly_expense': get_monthly_expense(request.user),
    }
    return render(request, 'bank/bank_home.html', context)


@login_required
def download_expenses(request):
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    expenses = CashFlow.objects.filter(
        user=request.user,
        cash_flow_type='expense',
        date__gte=week_ago
    ).order_by('date')

    content = "# Weekly Expenses\n\n"
    for entry in expenses:
        content += f"{entry.date} = ₹{entry.amount} [{entry.reason}]\n"

    response = HttpResponse(content, content_type='text/markdown')
    response['Content-Disposition'] = 'attachment; filename="weekly_expenses.md"'
    return response


@login_required
def download_income(request):
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    income = CashFlow.objects.filter(
        user=request.user,
        cash_flow_type='income',
        date__gte=month_start
    ).order_by('date')

    content = "# Monthly Income\n\n"
    for entry in income:
        content += f"{entry.date} = ₹{entry.amount} [{entry.reason}]\n"

    response = HttpResponse(content, content_type='text/markdown')
    response['Content-Disposition'] = 'attachment; filename="monthly_income.md"'
    return response


@login_required
def download_loans_taken(request):
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    loans = CashFlow.objects.filter(
        user=request.user,
        cash_flow_type='loan_taken',
        date__gte=month_start
    ).order_by('date')

    content = "# Monthly Loans Taken\n\n"
    for entry in loans:
        content += f"{entry.date} = ₹{entry.amount} from {entry.person}\n"

    response = HttpResponse(content, content_type='text/markdown')
    response['Content-Disposition'] = 'attachment; filename="monthly_loans_taken.md"'
    return response


@login_required
def download_loans_given(request):
    today = date.today()
    month_start = date(today.year, today.month, 1)
    
    loans = CashFlow.objects.filter(
        user=request.user,
        cash_flow_type='loan_given',
        date__gte=month_start
    ).order_by('date')

    content = "# Monthly Loans Given\n\n"
    for entry in loans:
        content += f"{entry.date} = ₹{entry.amount} to {entry.person}\n"

    response = HttpResponse(content, content_type='text/markdown')
    response['Content-Disposition'] = 'attachment; filename="monthly_loans_given.md"'
    return response

@login_required
def clear_loan(request, entry_id):
    loan = get_object_or_404(CashFlow, id=entry_id, user=request.user, status=CashFlow.PENDING)

    if loan.cash_flow_type not in [CashFlow.LOAN_GIVEN, CashFlow.LOAN_TAKEN]:
        return redirect('bank_home')

    loan.status = CashFlow.CLEARED
    loan.save()

    if loan.cash_flow_type == CashFlow.LOAN_GIVEN:
        CashFlow.objects.create(
            user=request.user,
            amount=loan.amount,
            person=loan.person,
            reason=f"Loan repaid by {loan.person}",
            cash_flow_type=CashFlow.INCOME,
            status=CashFlow.CLEARED,
        )
    else:
        CashFlow.objects.create(
            user=request.user,
            amount=loan.amount,
            person=loan.person,
            reason=f"Loan repaid to {loan.person}",
            cash_flow_type=CashFlow.EXPENSE,
            status=CashFlow.CLEARED,
        )

    messages.success(request, 'Loan cleared.')
    return redirect('bank_home')


def get_total_money(user):
    income = CashFlow.objects.filter(user=user, cash_flow_type='income', status='cleared').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = CashFlow.objects.filter(user=user, cash_flow_type='expense', status='cleared').aggregate(Sum('amount'))['amount__sum'] or 0
    
    return income - expense

def get_monthly_expense(user):
    today = date.today()
    result = CashFlow.objects.filter(
        user=user,
        cash_flow_type=CashFlow.EXPENSE,
        date__year=today.year,
        date__month=today.month,
    ).aggregate(Sum('amount'))
    return result['amount__sum'] or 0