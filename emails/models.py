from django.db import models
from django.utils import timezone
import uuid

class Campaign(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("delivered", "Delivered"),
        ("bounced", "Bounced"),
        ("opened", "Opened"),
        ("clicked", "Clicked"),
    ]

    email = models.EmailField()
    name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    opened = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class Campaign(models.Model):
    name = models.CharField(max_length=200)
    subject = models.CharField(max_length=300)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    total_sent = models.IntegerField(default=0)
   
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def get_stats(self):
        total = self.emails.count()
        opened = self.emails.filter(opened=True).count()
        clicked = self.emails.filter(clicked=True).count()
        bounced = self.emails.filter(bounced=True).count()
        
        return {
            'total': total,
            'opened': opened,
            'clicked': clicked,
            'bounced': bounced,
            'open_rate': (opened / total * 100) if total > 0 else 0,
            'click_rate': (clicked / total * 100) if total > 0 else 0,
            'bounce_rate': (bounced / total * 100) if total > 0 else 0,
        }


class Email(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='emails')
    recipient_email = models.EmailField()
    recipient_name = models.CharField(max_length=200)
    tracking_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    
    sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    opened = models.BooleanField(default=False)
    opened_at = models.DateTimeField(null=True, blank=True)
    open_count = models.IntegerField(default=0)
    
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(null=True, blank=True)
    click_count = models.IntegerField(default=0)
    
    bounced = models.BooleanField(default=False)
    bounced_at = models.DateTimeField(null=True, blank=True)
    bounce_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.recipient_email} - {self.campaign.name}"


class EmailEvent(models.Model):
    EVENT_TYPES = [
        ('sent', 'Sent'),
        ('opened', 'Opened'),
        ('clicked', 'Clicked'),
        ('bounced', 'Bounced'),
    ]
    
    email = models.ForeignKey(Email, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.event_type} - {self.email.recipient_email}"


class Recipient(models.Model):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.email})"



