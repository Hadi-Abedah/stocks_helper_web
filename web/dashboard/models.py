from django.db import models
from django.utils import timezone
    # Mirror of the CSV columns: Date, Account, Debit, Credit, Description

# Create your models here.

class Transaction(models.Model):
    transaction_id = models.CharField(max_length=64, primary_key=True)
    stock_symbol = models.CharField(max_length=10, null=True, blank=True)
    tx_type = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    fx_rate = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    currency = models.CharField(max_length=3, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    price  = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    units  = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    fee    = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    accounting_processed_at = models.DateTimeField(null=True, blank=True)

    def mark_accounting_processed(self):
        self.accounting_processed_at = timezone.now()
        self.save(update_fields=['accounting_processed_at'])

    def __str__(self):
        return f"{self.units} shares of {self.stock_symbol} at ${self.price} on {self.date}"
    class Meta:
        indexes = [
            models.Index(fields=['stock_symbol']),
            models.Index(fields=['tx_type']),
            models.Index(fields=['date']),
        ]


class Journal(models.Model):
    date = models.DateField(null=True, blank=True, db_index=True)
    account = models.CharField(max_length=128, db_index=True)
    debit = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    credit = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    description = models.TextField(blank=True)
    #line_no = models.PositiveIntegerField(null=True, blank=True)
    tx_id = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        
        return f"{self.description[:60]}"

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['account']),
        ]
        unique_together = ('date', 'account', 'debit', 'credit', 'description', 'tx_id')


class InvestmentLot(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='investment_lots')
    symbol = models.CharField(max_length=10, db_index=True)
    currency = models.CharField(max_length=3)
    price = models.DecimalField(max_digits=20, decimal_places=6)
    quantity_original = models.DecimalField(max_digits=20, decimal_places=6)
    quantity_remaining = models.DecimalField(max_digits=20, decimal_places=6)
    acquired_date = models.DateField()
    is_option = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity_remaining}/{self.quantity_original} {self.symbol} at {self.price}"

    class Meta:
        indexes = [
            models.Index(fields=['symbol', 'is_option', 'acquired_date']),
            models.Index(fields=['currency']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['transaction', 'symbol', 'is_option'],
                name='unique_investment_lot_transaction_symbol_option',
            ),
        ]
