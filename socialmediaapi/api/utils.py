from datetime import timedelta
from django.utils import timezone
from .models import Requests


SPECIAL_CHARECTERS = ["!","@","#","$","%","^","&","*","+","=","_","-","(",")","?","/","|"]

def has_reached_request_limit(user, limit=3, time_delta=timedelta(minutes=1)):
    current_time = timezone.now()
    threshold_time = current_time - time_delta

    total_requests_in_last_period = Requests.objects.filter(
        requested_at__gte=threshold_time, requested_at__lte=current_time, requested_by=user
    ).count()

    return total_requests_in_last_period >= limit

def is_password_strong_enough(password):
    if len(password) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in SPECIAL_CHARECTERS for char in password):
        return False

    return True
    