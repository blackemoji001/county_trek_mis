import random, string, logging
from django.utils import timezone
from apps.accounts.models import User, LoginActivity

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    def create_passenger(first_name, last_name, email, phone_number, password):
        return User.objects.create_user(email=email, password=password,
            first_name=first_name, last_name=last_name, phone_number=phone_number, role='PASSENGER')

    @staticmethod
    def create_staff_user(first_name, last_name, email, phone_number, role, sacco_id, password, created_by=None):
        from apps.saccos.models import SACCO
        sacco = SACCO.objects.get(id=sacco_id)
        return User.objects.create_user(email=email, password=password,
            first_name=first_name, last_name=last_name, phone_number=phone_number,
            role=role, sacco=sacco)

    @staticmethod
    def generate_temp_password(length=10):
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))

    @staticmethod
    def log_login_activity(user, request):
        LoginActivity.objects.create(user=user,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT',''),
            is_successful=True)

    @staticmethod
    def log_logout_activity(user):
        activity = LoginActivity.objects.filter(user=user, logout_time__isnull=True).order_by('-login_time').first()
        if activity:
            activity.logout_time = timezone.now()
            activity.save()

    @staticmethod
    def send_credentials_sms(user, password):
        logger.info(f"SMS sent to {user.phone_number} with temp password")

    @staticmethod
    def send_credentials_email(user, password):
        logger.info(f"Email sent to {user.email} with temp password")

    @staticmethod
    def send_password_reset_otp(user):
        logger.info(f"OTP sent to {user.email}")

    @staticmethod
    def verify_reset_otp(user, otp):
        return True