from django import template

register = template.Library()

@register.filter
def format_phone(phone_number):
    if not phone_number:
        return ''
    
    phone = str(phone_number)
    if len(phone) == 10:
        return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"
    return phone 