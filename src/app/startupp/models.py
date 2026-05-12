import uuid

from django.db import models


# Create your models here.
class StartupCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "startup_categories"

    def __str__(self):
        return self.name


class StartupStage(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "startup_stages"

    def __str__(self):
        return self.name


class Startup(models.Model):
    user_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    website_url = models.URLField()
    categories = models.ManyToManyField(StartupCategory)
    stages = models.ManyToManyField(StartupStage)
    founded_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "startups"

    def __str__(self):
        return self.name


class Campaign(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    raised_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_investment = models.DecimalField(max_digits=10, decimal_places=2)
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    burn_rate = models.DecimalField(max_digits=10, decimal_places=2)
    runway = models.DecimalField(max_digits=10, decimal_places=2)
    active_customers = models.IntegerField()
    valuation = models.DecimalField(max_digits=10, decimal_places=2)
    gross_margin = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=255)
    deadline = models.DateField()
    percentage = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "campaigns"

    def __str__(self):
        return self.startup.name


class BankInfo(models.Model):
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    receipient_name = models.CharField(max_length=255)
    mfo = models.CharField(max_length=255)

    class Meta:
        db_table = "bank_info"

    def __str__(self):
        return self.bank_name


class DocType:
    FINANCIAL_REPORT = "financial_report"
    BUSSINESS_PLAN = "business_plan"
    PRESENTATION = "presentation"
    LEGAL_DOCUMENT = "legal_document"

    DOCTYPE_CHOICES = [
        (FINANCIAL_REPORT, "Financial Report"),
        (BUSSINESS_PLAN, "Business Plan"),
        (PRESENTATION, "Presentation"),
        (LEGAL_DOCUMENT, "Legal Document"),
    ]


class Documents(models.Model):
    doc_type = models.CharField(max_length=255, choices=DocType.DOCTYPE_CHOICES)
    file_url = models.URLField()
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "startup_documents"

    def __str__(self):
        return self.title


class Investment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor_id = models.CharField(max_length=255)
    startup = models.ForeignKey(Startup, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    message = models.TextField(blank=True, default='')
    status = models.CharField(max_length=50, default='completed')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'investments'

    def __str__(self):
        return f'Investment {self.id} by {self.investor_id}'


class CompaignUpdate(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    body = models.TextField()
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "campaign_updates"

    def __str__(self):
        return self.title
