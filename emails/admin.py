from django.contrib import admin
from .models import Campaign, Email, EmailEvent, Recipient


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'total_sent', 'created_at', 'sent_at']
    search_fields = ['name', 'subject']
    list_filter = ['created_at', 'sent_at']


@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ['recipient_email', 'campaign', 'sent', 'opened', 'clicked', 'bounced']
    search_fields = ['recipient_email', 'recipient_name']
    list_filter = ['sent', 'opened', 'clicked', 'bounced', 'created_at']


@admin.register(EmailEvent)
class EmailEventAdmin(admin.ModelAdmin):
    list_display = ['email', 'event_type', 'timestamp', 'ip_address']
    list_filter = ['event_type', 'timestamp']


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    search_fields = ['name', 'email']
