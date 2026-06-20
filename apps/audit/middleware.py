import json
from apps.audit.models import AuditLog

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and request.method in ['POST','PUT','DELETE']:
            AuditLog.objects.create(
                user=request.user,
                action=request.method,
                model_name=request.path.split('/')[1] if len(request.path.split('/'))>1 else '',
                object_id='',
                changes=json.dumps({'path':request.path}),
                ip_address=request.META.get('REMOTE_ADDR')
            )
        return response