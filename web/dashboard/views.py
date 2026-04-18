from django.shortcuts import render
from .models import Transaction, Journal
# Create your views here.


def dashboard(request):
    # get every stock symbol in every transaction
    stock_symbols = Transaction.objects.values_list('stock_symbol', flat=True).distinct()
    return render(request, 'dashboard/home.html', {'stock_symbols': stock_symbols})


def stock_detail(request, stock_symbol):
    transactions = Transaction.objects.filter(stock_symbol=stock_symbol).order_by('date')
    return render(request, 'dashboard/stock_detail.html', {'transactions': transactions})