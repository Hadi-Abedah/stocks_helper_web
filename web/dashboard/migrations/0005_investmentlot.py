# Generated manually for DB-backed SnapTrade lot tracking.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_remove_journal_line_no'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='stock_symbol',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='tx_type',
            field=models.CharField(max_length=32),
        ),
        migrations.AddField(
            model_name='transaction',
            name='accounting_processed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='InvestmentLot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('symbol', models.CharField(db_index=True, max_length=10)),
                ('currency', models.CharField(max_length=3)),
                ('price', models.DecimalField(decimal_places=6, max_digits=20)),
                ('quantity_original', models.DecimalField(decimal_places=6, max_digits=20)),
                ('quantity_remaining', models.DecimalField(decimal_places=6, max_digits=20)),
                ('acquired_date', models.DateField()),
                ('is_option', models.BooleanField(default=False)),
                ('transaction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='investment_lots', to='dashboard.transaction')),
            ],
        ),
        migrations.AddIndex(
            model_name='investmentlot',
            index=models.Index(fields=['symbol', 'is_option', 'acquired_date'], name='dashboard_i_symbol_a4bb20_idx'),
        ),
        migrations.AddIndex(
            model_name='investmentlot',
            index=models.Index(fields=['currency'], name='dashboard_i_currenc_43c652_idx'),
        ),
        migrations.AddConstraint(
            model_name='investmentlot',
            constraint=models.UniqueConstraint(fields=('transaction', 'symbol', 'is_option'), name='unique_investment_lot_transaction_symbol_option'),
        ),
    ]
