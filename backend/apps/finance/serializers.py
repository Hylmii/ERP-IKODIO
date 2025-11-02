"""
Finance & Accounting serializers
"""
from rest_framework import serializers
from django.db.models import Sum, Q
from apps.finance.models import (
    GeneralLedger, JournalEntry, JournalEntryLine,
    Invoice, InvoiceLine, Payment, Expense,
    Budget, BudgetLine, Tax
)


# ============ General Ledger ============

class GeneralLedgerListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for GL list"""
    sub_account_count = serializers.SerializerMethodField()
    transaction_count = serializers.SerializerMethodField()
    
    class Meta:
        model = GeneralLedger
        fields = [
            'id', 'code', 'name', 'account_type', 'parent',
            'is_active', 'is_header', 'currency', 'balance',
            'sub_account_count', 'transaction_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_sub_account_count(self, obj):
        return obj.sub_accounts.count()
    
    def get_transaction_count(self, obj):
        return obj.journal_lines.count()


class GeneralLedgerSerializer(serializers.ModelSerializer):
    """Full GL account serializer"""
    parent_name = serializers.CharField(source='parent.name', read_only=True)
    sub_accounts = GeneralLedgerListSerializer(many=True, read_only=True)
    
    class Meta:
        model = GeneralLedger
        fields = [
            'id', 'code', 'name', 'description', 'account_type',
            'parent', 'parent_name', 'is_active', 'is_header',
            'currency', 'balance', 'sub_accounts',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


# ============ Journal Entry ============

class JournalEntryLineSerializer(serializers.ModelSerializer):
    """Journal entry line serializer"""
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = JournalEntryLine
        fields = [
            'id', 'account', 'account_code', 'account_name',
            'description', 'debit', 'credit',
            'project', 'project_name', 'department', 'department_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class JournalEntryListSerializer(serializers.ModelSerializer):
    """Lightweight journal entry list"""
    posted_by_name = serializers.CharField(source='posted_by.full_name', read_only=True)
    total_debit = serializers.SerializerMethodField()
    total_credit = serializers.SerializerMethodField()
    is_balanced = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_number', 'entry_date', 'description',
            'status', 'posted_by_name', 'posted_at',
            'total_debit', 'total_credit', 'is_balanced',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_debit(self, obj):
        return obj.lines.aggregate(total=Sum('debit'))['total'] or 0
    
    def get_total_credit(self, obj):
        return obj.lines.aggregate(total=Sum('credit'))['total'] or 0
    
    def get_is_balanced(self, obj):
        total_debit = self.get_total_debit(obj)
        total_credit = self.get_total_credit(obj)
        return total_debit == total_credit


class JournalEntrySerializer(serializers.ModelSerializer):
    """Full journal entry serializer"""
    lines = JournalEntryLineSerializer(many=True, read_only=True)
    posted_by_name = serializers.CharField(source='posted_by.full_name', read_only=True)
    total_debit = serializers.SerializerMethodField()
    total_credit = serializers.SerializerMethodField()
    is_balanced = serializers.SerializerMethodField()
    
    class Meta:
        model = JournalEntry
        fields = [
            'id', 'entry_number', 'entry_date', 'description',
            'reference_number', 'status', 'lines',
            'posted_by', 'posted_by_name', 'posted_at',
            'reversed_entry', 'reversed_at', 'attachments',
            'total_debit', 'total_credit', 'is_balanced',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'posted_at', 'reversed_at', 'created_at', 'updated_at', 'deleted_at']
    
    def get_total_debit(self, obj):
        return obj.lines.aggregate(total=Sum('debit'))['total'] or 0
    
    def get_total_credit(self, obj):
        return obj.lines.aggregate(total=Sum('credit'))['total'] or 0
    
    def get_is_balanced(self, obj):
        total_debit = self.get_total_debit(obj)
        total_credit = self.get_total_credit(obj)
        return total_debit == total_credit


# ============ Invoice ============

class InvoiceLineSerializer(serializers.ModelSerializer):
    """Invoice line item serializer"""
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = InvoiceLine
        fields = [
            'id', 'description', 'quantity', 'unit_price',
            'discount_percentage', 'tax_percentage', 'amount',
            'account', 'account_code', 'account_name', 'line_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight invoice list"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    days_overdue = serializers.SerializerMethodField()
    payment_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'invoice_date', 'due_date',
            'client', 'client_name', 'project_name', 'status',
            'total_amount', 'paid_amount', 'outstanding_amount', 'currency',
            'days_overdue', 'payment_progress',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_overdue(self, obj):
        if obj.status in ['paid', 'cancelled']:
            return 0
        from django.utils import timezone
        if obj.due_date < timezone.now().date():
            return (timezone.now().date() - obj.due_date).days
        return 0
    
    def get_payment_progress(self, obj):
        if obj.total_amount == 0:
            return 0
        return round((obj.paid_amount / obj.total_amount) * 100, 2)


class InvoiceSerializer(serializers.ModelSerializer):
    """Full invoice serializer"""
    lines = InvoiceLineSerializer(many=True, read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    days_overdue = serializers.SerializerMethodField()
    payment_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'invoice_type', 'invoice_date', 'due_date',
            'client', 'client_name', 'project', 'project_name',
            'subtotal', 'tax_amount', 'discount_amount', 'total_amount',
            'paid_amount', 'outstanding_amount', 'currency',
            'tax_percentage', 'tax_number', 'status',
            'payment_terms', 'notes', 'internal_notes',
            'invoice_file', 'lines', 'days_overdue', 'payment_progress',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
    
    def get_days_overdue(self, obj):
        if obj.status in ['paid', 'cancelled']:
            return 0
        from django.utils import timezone
        if obj.due_date < timezone.now().date():
            return (timezone.now().date() - obj.due_date).days
        return 0
    
    def get_payment_progress(self, obj):
        if obj.total_amount == 0:
            return 0
        return round((obj.paid_amount / obj.total_amount) * 100, 2)


# ============ Payment ============

class PaymentListSerializer(serializers.ModelSerializer):
    """Lightweight payment list"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'payment_type', 'payment_date',
            'client_name', 'invoice_number', 'amount', 'currency',
            'payment_method', 'status', 'account_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Full payment serializer"""
    client_name = serializers.CharField(source='client.name', read_only=True)
    invoice_number = serializers.CharField(source='invoice.invoice_number', read_only=True)
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'payment_number', 'payment_type', 'payment_date',
            'client', 'client_name', 'invoice', 'invoice_number',
            'amount', 'currency', 'payment_method', 'reference_number',
            'bank_name', 'bank_account', 'status',
            'account', 'account_code', 'account_name',
            'notes', 'attachments',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']


# ============ Expense ============

class ExpenseListSerializer(serializers.ModelSerializer):
    """Lightweight expense list"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_number', 'expense_date', 'category',
            'description', 'amount', 'currency', 'status',
            'employee_name', 'project_name', 'department_name',
            'approved_by_name', 'approved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ExpenseSerializer(serializers.ModelSerializer):
    """Full expense serializer"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_number', 'expense_date', 'category',
            'description', 'amount', 'currency',
            'employee', 'employee_name',
            'project', 'project_name', 'department', 'department_name',
            'account', 'account_code', 'account_name',
            'status', 'approved_by', 'approved_by_name', 'approved_at',
            'approval_notes', 'paid_at', 'payment_reference',
            'attachments',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'approved_at', 'paid_at', 'created_at', 'updated_at', 'deleted_at']


# ============ Budget ============

class BudgetLineSerializer(serializers.ModelSerializer):
    """Budget line item serializer"""
    account_code = serializers.CharField(source='account.code', read_only=True)
    account_name = serializers.CharField(source='account.name', read_only=True)
    remaining_amount = serializers.ReadOnlyField()
    utilization_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = BudgetLine
        fields = [
            'id', 'account', 'account_code', 'account_name',
            'allocated_amount', 'spent_amount', 'committed_amount',
            'remaining_amount', 'utilization_percentage', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_utilization_percentage(self, obj):
        if obj.allocated_amount == 0:
            return 0
        utilized = obj.spent_amount + obj.committed_amount
        return round((utilized / obj.allocated_amount) * 100, 2)


class BudgetListSerializer(serializers.ModelSerializer):
    """Lightweight budget list"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    remaining_budget = serializers.SerializerMethodField()
    utilization_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'fiscal_year', 'start_date', 'end_date',
            'department_name', 'project_name', 'status',
            'total_budget', 'total_spent', 'total_committed',
            'remaining_budget', 'utilization_percentage',
            'approved_by_name', 'approved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_remaining_budget(self, obj):
        return obj.total_budget - obj.total_spent - obj.total_committed
    
    def get_utilization_percentage(self, obj):
        if obj.total_budget == 0:
            return 0
        utilized = obj.total_spent + obj.total_committed
        return round((utilized / obj.total_budget) * 100, 2)


class BudgetSerializer(serializers.ModelSerializer):
    """Full budget serializer"""
    lines = BudgetLineSerializer(many=True, read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    remaining_budget = serializers.SerializerMethodField()
    utilization_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Budget
        fields = [
            'id', 'name', 'description', 'fiscal_year',
            'start_date', 'end_date',
            'department', 'department_name', 'project', 'project_name',
            'total_budget', 'total_spent', 'total_committed',
            'remaining_budget', 'utilization_percentage', 'currency',
            'status', 'approved_by', 'approved_by_name', 'approved_at',
            'lines',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'approved_at', 'created_at', 'updated_at', 'deleted_at']
    
    def get_remaining_budget(self, obj):
        return obj.total_budget - obj.total_spent - obj.total_committed
    
    def get_utilization_percentage(self, obj):
        if obj.total_budget == 0:
            return 0
        utilized = obj.total_spent + obj.total_committed
        return round((utilized / obj.total_budget) * 100, 2)


# ============ Tax ============

class TaxSerializer(serializers.ModelSerializer):
    """Tax management serializer"""
    tax_type_display = serializers.CharField(source='get_tax_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Tax
        fields = [
            'id', 'tax_number', 'tax_type', 'tax_type_display',
            'tax_period_month', 'tax_period_year',
            'taxable_amount', 'tax_rate', 'tax_amount',
            'status', 'status_display',
            'filing_date', 'payment_date', 'reference_number',
            'tax_report', 'notes',
            'created_at', 'updated_at', 'deleted_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'deleted_at']
