import re
from django.core.exceptions import ValidationError

class ComplexPasswordValidator:
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.findall('[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.findall('[0-9]', password):
            raise ValidationError('Password must contain at least one digit.')
        if not re.findall('[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError('Password must contain at least one special character.')

    def get_help_text(self):
        return "Must contain uppercase, lowercase, number, and special character."