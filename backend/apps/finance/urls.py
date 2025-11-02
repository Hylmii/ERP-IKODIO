"""
Finance & Accounting URLs
"""
from django.urls import path
from apps.finance import views

app_name = 'finance'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.finance_dashboard, name='finance-dashboard'),
    
    # General Ledger
    path('accounts/', views.GeneralLedgerListView.as_view(), name='gl-list'),
    path('accounts/<int:pk>/', views.GeneralLedgerDetailView.as_view(), name='gl-detail'),
    
    # Journal Entries
    path('journal-entries/', views.JournalEntryListView.as_view(), name='journal-list'),
    path('journal-entries/<int:pk>/', views.JournalEntryDetailView.as_view(), name='journal-detail'),
    path('journal-entries/<int:pk>/post/', views.journal_entry_post, name='journal-post'),
    
    # Invoices
    path('invoices/', views.InvoiceListView.as_view(), name='invoice-list'),
    path('invoices/<int:pk>/', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    
    # Payments
    path('payments/', views.PaymentListView.as_view(), name='payment-list'),
    path('payments/<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('payments/<int:pk>/confirm/', views.payment_confirm, name='payment-confirm'),
    
    # Expenses
    path('expenses/', views.ExpenseListView.as_view(), name='expense-list'),
    path('expenses/<int:pk>/', views.ExpenseDetailView.as_view(), name='expense-detail'),
    path('expenses/<int:pk>/approve/', views.expense_approve, name='expense-approve'),
    path('expenses/<int:pk>/reject/', views.expense_reject, name='expense-reject'),
    
    # Budgets
    path('budgets/', views.BudgetListView.as_view(), name='budget-list'),
    path('budgets/<int:pk>/', views.BudgetDetailView.as_view(), name='budget-detail'),
    
    # Taxes
    path('taxes/', views.TaxListView.as_view(), name='tax-list'),
    path('taxes/<int:pk>/', views.TaxDetailView.as_view(), name='tax-detail'),
]
