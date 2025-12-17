from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
from django.db.models import Count, Q
from .models import Campaign, Email, EmailEvent, Recipient
import base64
from io import BytesIO

   
def dashboard(request):
    campaigns = Campaign.objects.all()[:10]
    
    total_campaigns = Campaign.objects.count()
    total_emails = Email.objects.count()
    total_opened = Email.objects.filter(opened=True).count()
    total_clicked = Email.objects.filter(clicked=True).count()
    
    open_rate = (total_opened / total_emails * 100) if total_emails > 0 else 0
    click_rate = (total_clicked / total_emails * 100) if total_emails > 0 else 0
    
    context = {
        'campaigns': campaigns,
        'stats': {
            'total_campaigns': total_campaigns,
            'total_emails': total_emails,
            'total_opened': total_opened,
            'total_clicked': total_clicked,
            'open_rate': round(open_rate, 2),
            'click_rate': round(click_rate, 2),
        }
    }
    return render(request, 'index.html', context)


def campaign_list(request):
    campaigns = Campaign.objects.all()
    campaigns_data = []
    
    for campaign in campaigns:
        stats = campaign.get_stats()
        campaigns_data.append({
            'campaign': campaign,
            'stats': stats
        })
    
    context = {'campaigns_data': campaigns_data}
    return render(request, 'campaign_list.html', context)


def campaign_detail(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    emails = campaign.emails.all()
    stats = campaign.get_stats()
    
    context = {
        'campaign': campaign,
        'emails': emails,
        'stats': stats,
    }
    return render(request, 'campaign_detail.html', context)


def create_campaign(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        subject = request.POST.get('subject')
        content = request.POST.get('content')
        
        campaign = Campaign.objects.create(
            name=name,
            subject=subject,
            content=content
        )
        
        messages.success(request, 'Campaign created successfully!')
        return redirect('campaign_detail', pk=campaign.pk)
    
    recipients = Recipient.objects.all()
    return render(request, 'send_email.html', {'recipients': recipients})


def send_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        recipient_ids = request.POST.getlist('recipients')
        recipients = Recipient.objects.filter(id__in=recipient_ids)
        
        sent_count = 0
        for recipient in recipients:
            # Create email record
            email = Email.objects.create(
                campaign=campaign,
                recipient_email=recipient.email,
                recipient_name=recipient.name
            )
            
            # Generate tracking content
            tracking_pixel = f'<img src="{request.build_absolute_uri(f"/track/open/{email.tracking_id}/")}" width="1" height="1" />'
            tracked_content = campaign.content.replace('</body>', f'{tracking_pixel}</body>')
            
            # Replace links with tracked links
            import re
            def replace_link(match):
                url = match.group(1)
                tracked_url = request.build_absolute_uri(f'/track/click/{email.tracking_id}/?url={url}')
                return f'href="{tracked_url}"'
            
            tracked_content = re.sub(r'href="([^"]+)"', replace_link, tracked_content)
            
            # Send email
            try:
                send_mail(
                    campaign.subject,
                    'hello',
                    "gayathrimr8489@gmail.com",
                    [recipient.email],
                    fail_silently=False,
                    html_message=tracked_content,
                )
                
                email.sent = True
                email.sent_at = timezone.now()
                email.save()
                
                EmailEvent.objects.create(
                    email=email,
                    event_type='sent'
                )
                
                sent_count += 1
            except Exception as e:
                email.bounced = True
                email.bounced_at = timezone.now()
                email.bounce_reason = str(e)
                email.save()
                
                EmailEvent.objects.create(
                    email=email,
                    event_type='bounced',
                    metadata={'error': str(e)}
                )
        
        campaign.total_sent = sent_count
        campaign.sent_at = timezone.now()
        campaign.save()
        
        messages.success(request, f'Campaign sent to {sent_count} recipients!')
        return redirect('campaign_detail', pk=campaign.pk)
    
    recipients = Recipient.objects.all()
    return render(request, 'send_campaign.html', {
        'campaign': campaign,
        'recipients': recipients
    })


def track_open(request, tracking_id):
    try:
        email = Email.objects.get(tracking_id=tracking_id)
        
        if not email.opened:
            email.opened = True
            email.opened_at = timezone.now()
        
        email.open_count += 1
        email.save()
        
        # Get client info
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        EmailEvent.objects.create(
            email=email,
            event_type='opened',
            ip_address=ip,
            user_agent=user_agent
        )
    except Email.DoesNotExist:
        pass
    
    # Return 1x1 transparent pixel
    pixel = base64.b64decode('R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7')
    return HttpResponse(pixel, content_type='image/gif')


def track_click(request, tracking_id):
    url = request.GET.get('url', '/')
    
    try:
        email = Email.objects.get(tracking_id=tracking_id)
        
        if not email.clicked:
            email.clicked = True
            email.clicked_at = timezone.now()
        
        email.click_count += 1
        email.save()
        
        ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        EmailEvent.objects.create(
            email=email,
            event_type='clicked',
            ip_address=ip,
            user_agent=user_agent,
            metadata={'url': url}
        )
    except Email.DoesNotExist:
        pass
    
    return redirect(url)


def add_recipient(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        name = request.POST.get('name')
        
        Recipient.objects.get_or_create(
            email=email,
            defaults={'name': name}
        )
        
        messages.success(request, 'Recipient added successfully!')
        return redirect('create_campaign')
    
    return redirect('index')