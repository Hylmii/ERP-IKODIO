"""
Finance & Accounting views
"""
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.authentication.permissions import IsAdminOrReadOnly
from apps.finance.models import (
    GeneralLedger, JournalEntry, JournalEntryLine,
    Invoice, InvoiceLine, Payment, Expense,
    Budget, BudgetLine, Tax
)
from apps.finance.serializers import (
    GeneralLedgerListSerializer, GeneralLedgerSerializer,
    JournalEntryListSerializer, JournalEntrySerializer, JournalEntryLineSerializer,
    InvoiceListSerializer, InvoiceSerializer, InvoiceLineSerializer,
    PaymentListSerializer, PaymentSerializer,
    ExpenseListSerializer, ExpenseSerializer,
    BudgetListSerializer, BudgetSerializer, BudgetLineSerializer,
    TaxSerializer
)


# ============ General Ledger ============

class GeneralLedgerListView(generics.ListCreateAPIView):
    """List and create GL accounts"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = GeneralLedgerListSerializer
    
    def get_queryset(self):
        queryset = GeneralLedger.objects.filter(deleted_at__isnull=True)
        
        # Filter by account type
        account_type = self.request.query_params.get('account_type')
        if account_type:
            queryset = queryset.filter(account_type=account_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter header accounts
        is_header = self.request.query_params.get('is_header')
        if is_header is not None:
            queryset = queryset.filter(is_header=is_header.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(code__icontains=search) |
                Q(name__icontains=search)
            )
        
        return queryset.select_related('parent').order_by('code')


class GeneralLedgerDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete GL account"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = GeneralLedgerSerializer
    
    def get_queryset(self):
        return GeneralLedger.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Journal Entry ============

class JournalEntryListView(generics.ListCreateAPIView):
    """List and create journal entries"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = JournalEntryListSerializer
    
    def get_queryset(self):
        queryset = JournalEntry.objects.filter(deleted_at__isnull=True)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(entry_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(entry_date__lte=end_date)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(entry_number__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('posted_by').prefetch_related('lines')


class JournalEntryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete journal entry"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = JournalEntrySerializer
    
    def get_queryset(self):
        return JournalEntry.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def journal_entry_post(request, pk):
    """Post a journal entry (make it permanent)"""
    try:
        journal_entry = JournalEntry.objects.get(pk=pk, deleted_at__isnull=True)
    except JournalEntry.DoesNotExist:
        return Response(
            {'error': 'Journal entry not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if journal_entry.status != 'draft':
        return Response(
            {'error': 'Only draft entries can be posted'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate balanced entry
    total_debit = journal_entry.lines.aggregate(total=Sum('debit'))['total'] or 0
    total_credit = journal_entry.lines.aggregate(total=Sum('credit'))['total'] or 0
    
    if total_debit != total_credit:
        return Response(
            {'error': f'Journal entry is not balanced. Debit: {total_debit}, Credit: {total_credit}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Post the entry
    journal_entry.status = 'posted'
    journal_entry.posted_at = timezone.now()
    journal_entry.posted_by = request.user.employee_profile
    journal_entry.save()
    
    # Update GL account balances
    for line in journal_entry.lines.all():
        account = line.account
        if line.debit > 0:
            if account.account_type in ['asset', 'expense']:
                account.balance += line.debit
            else:
                account.balance -= line.debit
        if line.credit > 0:
            if account.account_type in ['asset', 'expense']:
                account.balance -= line.credit
            else:
                account.balance += line.credit
        account.save()
    
    serializer = JournalEntrySerializer(journal_entry)
    return Response(serializer.data)


# ============ Invoice ============

class InvoiceListView(generics.ListCreateAPIView):
    """List and create invoices"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = InvoiceListSerializer
    
    def get_queryset(self):
        queryset = Invoice.objects.filter(deleted_at__isnull=True)
        
        # Filter by type
        invoice_type = self.request.query_params.get('type')
        if invoice_type:
            queryset = queryset.filter(invoice_type=invoice_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by client
        client = self.request.query_params.get('client')
        if client:
            queryset = queryset.filter(client_id=client)
        
        # Filter overdue
        overdue = self.request.query_params.get('overdue')
        if overdue and overdue.lower() == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now().date(),
                status__in=['sent', 'partial']
            )
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(invoice_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(invoice_date__lte=end_date)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(client__name__icontains=search)
            )
        
        return queryset.select_related('client', 'project').prefetch_related('lines')


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete invoice"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = InvoiceSerializer
    
    def get_queryset(self):
        return Invoice.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Payment ============

class PaymentListView(generics.ListCreateAPIView):
    """List and create payments"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = PaymentListSerializer
    
    def get_queryset(self):
        queryset = Payment.objects.filter(deleted_at__isnull=True)
        
        # Filter by type
        payment_type = self.request.query_params.get('type')
        if payment_type:
            queryset = queryset.filter(payment_type=payment_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by client
        client = self.request.query_params.get('client')
        if client:
            queryset = queryset.filter(client_id=client)
        
        # Filter by invoice
        invoice = self.request.query_params.get('invoice')
        if invoice:
            queryset = queryset.filter(invoice_id=invoice)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(payment_number__icontains=search) |
                Q(reference_number__icontains=search)
            )
        
        return queryset.select_related('client', 'invoice', 'account')


class PaymentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete payment"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = PaymentSerializer
    
    def get_queryset(self):
        return Payment.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def payment_confirm(request, pk):
    """Confirm a payment and update invoice"""
    try:
        payment = Payment.objects.get(pk=pk, deleted_at__isnull=True)
    except Payment.DoesNotExist:
        return Response(
            {'error': 'Payment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if payment.status != 'pending':
        return Response(
            {'error': 'Only pending payments can be confirmed'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update payment status
    payment.status = 'completed'
    payment.save()
    
    # Update invoice if linked
    if payment.invoice:
        invoice = payment.invoice
        invoice.paid_amount += payment.amount
        invoice.outstanding_amount = invoice.total_amount - invoice.paid_amount
        
        # Update invoice status
        if invoice.outstanding_amount <= 0:
            invoice.status = 'paid'
        elif invoice.paid_amount > 0:
            invoice.status = 'partial'
        
        invoice.save()
    
    serializer = PaymentSerializer(payment)
    return Response(serializer.data)


# ============ Expense ============

class ExpenseListView(generics.ListCreateAPIView):
    """List and create expenses"""
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseListSerializer
    
    def get_queryset(self):
        queryset = Expense.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their expenses
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(employee=user.employee_profile)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by employee
        employee = self.request.query_params.get('employee')
        if employee:
            queryset = queryset.filter(employee_id=employee)
        
        # Filter by project
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project_id=project)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(expense_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(expense_date__lte=end_date)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(expense_number__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related(
            'employee', 'project', 'department', 'account', 'approved_by'
        )


class ExpenseDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete expense"""
    permission_classes = [IsAuthenticated]
    serializer_class = ExpenseSerializer
    
    def get_queryset(self):
        queryset = Expense.objects.filter(deleted_at__isnull=True)
        user = self.request.user
        
        # Non-admin users see only their expenses
        if not user.is_staff and hasattr(user, 'employee_profile'):
            queryset = queryset.filter(employee=user.employee_profile)
        
        return queryset
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def expense_approve(request, pk):
    """Approve an expense"""
    try:
        expense = Expense.objects.get(pk=pk, deleted_at__isnull=True)
    except Expense.DoesNotExist:
        return Response(
            {'error': 'Expense not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if expense.status != 'submitted':
        return Response(
            {'error': 'Only submitted expenses can be approved'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Approve expense
    expense.status = 'approved'
    expense.approved_by = request.user.employee_profile
    expense.approved_at = timezone.now()
    expense.approval_notes = request.data.get('approval_notes', '')
    expense.save()
    
    serializer = ExpenseSerializer(expense)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def expense_reject(request, pk):
    """Reject an expense"""
    try:
        expense = Expense.objects.get(pk=pk, deleted_at__isnull=True)
    except Expense.DoesNotExist:
        return Response(
            {'error': 'Expense not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if expense.status != 'submitted':
        return Response(
            {'error': 'Only submitted expenses can be rejected'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Reject expense
    expense.status = 'rejected'
    expense.approved_by = request.user.employee_profile
    expense.approved_at = timezone.now()
    expense.approval_notes = request.data.get('approval_notes', '')
    expense.save()
    
    serializer = ExpenseSerializer(expense)
    return Response(serializer.data)


# ============ Budget ============

class BudgetListView(generics.ListCreateAPIView):
    """List and create budgets"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = BudgetListSerializer
    
    def get_queryset(self):
        queryset = Budget.objects.filter(deleted_at__isnull=True)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by fiscal year
        fiscal_year = self.request.query_params.get('fiscal_year')
        if fiscal_year:
            queryset = queryset.filter(fiscal_year=fiscal_year)
        
        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department_id=department)
        
        # Filter by project
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project_id=project)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.select_related('department', 'project', 'approved_by')


class BudgetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete budget"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = BudgetSerializer
    
    def get_queryset(self):
        return Budget.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Tax ============

class TaxListView(generics.ListCreateAPIView):
    """List and create taxes"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = TaxSerializer
    
    def get_queryset(self):
        queryset = Tax.objects.filter(deleted_at__isnull=True)
        
        # Filter by type
        tax_type = self.request.query_params.get('type')
        if tax_type:
            queryset = queryset.filter(tax_type=tax_type)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(tax_period_year=year)
        
        # Filter by month
        month = self.request.query_params.get('month')
        if month:
            queryset = queryset.filter(tax_period_month=month)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(tax_number__icontains=search)
        
        return queryset.order_by('-tax_period_year', '-tax_period_month')


class TaxDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete tax"""
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    serializer_class = TaxSerializer
    
    def get_queryset(self):
        return Tax.objects.filter(deleted_at__isnull=True)
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.deleted_at = timezone.now()
        instance.save()


# ============ Dashboard ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finance_dashboard(request):
    """Finance dashboard with key metrics"""
    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_year = today.year
    
    # Revenue metrics (from invoices)
    invoices = Invoice.objects.filter(
        deleted_at__isnull=True,
        invoice_type='sales'
    )
    
    total_revenue = invoices.filter(status='paid').aggregate(
        total=Coalesce(Sum('total_amount'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    outstanding_ar = invoices.exclude(status__in=['paid', 'cancelled']).aggregate(
        total=Coalesce(Sum('outstanding_amount'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    overdue_invoices = invoices.filter(
        due_date__lt=today,
        status__in=['sent', 'partial']
    ).count()
    
    # Monthly revenue trend
    monthly_revenue = invoices.filter(
        invoice_date__year=current_year,
        status='paid'
    ).values('invoice_date__month').annotate(
        revenue=Coalesce(Sum('total_amount'), Decimal('0'), output_field=DecimalField())
    ).order_by('invoice_date__month')
    
    # Expense metrics
    expenses = Expense.objects.filter(deleted_at__isnull=True)
    
    total_expenses = expenses.filter(status='paid').aggregate(
        total=Coalesce(Sum('amount'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    pending_expenses = expenses.filter(status='submitted').count()
    
    # Monthly expenses
    monthly_expenses = expenses.filter(
        expense_date__year=current_year,
        status='paid'
    ).values('expense_date__month').annotate(
        amount=Coalesce(Sum('amount'), Decimal('0'), output_field=DecimalField())
    ).order_by('expense_date__month')
    
    # Budget utilization
    active_budgets = Budget.objects.filter(
        deleted_at__isnull=True,
        status='active',
        start_date__lte=today,
        end_date__gte=today
    )
    
    budget_summary = active_budgets.aggregate(
        total_budget=Coalesce(Sum('total_budget'), Decimal('0'), output_field=DecimalField()),
        total_spent=Coalesce(Sum('total_spent'), Decimal('0'), output_field=DecimalField()),
        total_committed=Coalesce(Sum('total_committed'), Decimal('0'), output_field=DecimalField())
    )
    
    # Cash flow (simplified)
    cash_in = Payment.objects.filter(
        deleted_at__isnull=True,
        payment_type='receipt',
        status='completed',
        payment_date__gte=current_month_start
    ).aggregate(
        total=Coalesce(Sum('amount'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    cash_out = Payment.objects.filter(
        deleted_at__isnull=True,
        payment_type='payment',
        status='completed',
        payment_date__gte=current_month_start
    ).aggregate(
        total=Coalesce(Sum('amount'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    # Tax obligations
    pending_taxes = Tax.objects.filter(
        deleted_at__isnull=True,
        status='calculated'
    ).aggregate(
        total=Coalesce(Sum('tax_amount'), Decimal('0'), output_field=DecimalField())
    )['total']
    
    return Response({
        'revenue': {
            'total': float(total_revenue),
            'outstanding_ar': float(outstanding_ar),
            'overdue_invoices': overdue_invoices,
            'monthly_trend': [
                {
                    'month': item['invoice_date__month'],
                    'revenue': float(item['revenue'])
                }
                for item in monthly_revenue
            ]
        },
        'expenses': {
            'total': float(total_expenses),
            'pending_approval': pending_expenses,
            'monthly_trend': [
                {
                    'month': item['expense_date__month'],
                    'amount': float(item['amount'])
                }
                for item in monthly_expenses
            ]
        },
        'budget': {
            'total_budget': float(budget_summary['total_budget']),
            'total_spent': float(budget_summary['total_spent']),
            'total_committed': float(budget_summary['total_committed']),
            'remaining': float(
                budget_summary['total_budget'] - 
                budget_summary['total_spent'] - 
                budget_summary['total_committed']
            )
        },
        'cash_flow': {
            'cash_in_this_month': float(cash_in),
            'cash_out_this_month': float(cash_out),
            'net_cash_flow': float(cash_in - cash_out)
        },
        'tax': {
            'pending_obligations': float(pending_taxes)
        }
    })
