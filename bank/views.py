from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import CashFlow
from .forms import CashFlowForm
from datetime import date

@login_required
def bank_home(request):
    if request.method == 'POST':
        form = CashFlowForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            if entry.cash_flow_type in [CashFlow.INCOME, CashFlow.EXPENSE]:
                entry.status = CashFlow.CLEARED
            entry.save()
            return redirect('bank_home')
    else:
        form = CashFlowForm()

    income = CashFlow.objects.filter(user=request.user, cash_flow_type=CashFlow.INCOME)
    expense = CashFlow.objects.filter(user=request.user, cash_flow_type=CashFlow.EXPENSE)
    loan_given = CashFlow.objects.filter(user=request.user, cash_flow_type=CashFlow.LOAN_GIVEN)
    loan_taken = CashFlow.objects.filter(user=request.user, cash_flow_type=CashFlow.LOAN_TAKEN)

    context = {
        'form': form,
        'income': income,
        'expense': expense,
        'loan_given': loan_given,
        'loan_taken': loan_taken,
    }
    return render(request, 'bank/bank_home.html', context)


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
    def total_for(cf_type):
        result = CashFlow.objects.filter(user=user, cash_flow_type=cf_type).aggregate(Sum('amount'))
        return result['amount__sum'] or 0

    income = total_for(CashFlow.INCOME)
    expense = total_for(CashFlow.EXPENSE)
    loan_given = total_for(CashFlow.LOAN_GIVEN)
    loan_taken = total_for(CashFlow.LOAN_TAKEN)

    return income + loan_taken - expense - loan_given

def get_monthly_expense(user):
    today = date.today()
    result = CashFlow.objects.filter(
        user=user,
        cash_flow_type=CashFlow.EXPENSE,
        date__year=today.year,
        date__month=today.month,
    ).aggregate(Sum('amount'))
    return result['amount__sum'] or 0