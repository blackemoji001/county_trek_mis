# payments services
import base64
import requests
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MpesaService:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.passkey = settings.MPESA_PASSKEY
        self.shortcode = settings.MPESA_SHORTCODE
        self.env = settings.MPESA_ENVIRONMENT
        self.base_url = 'https://api.safaricom.co.ke' if self.env == 'production' else 'https://sandbox.safaricom.co.ke'

    def get_token(self):
        r = requests.get(f'{self.base_url}/oauth/v1/generate?grant_type=client_credentials',
                         auth=(self.consumer_key, self.consumer_secret))
        return r.json().get('access_token')

    def stk_push(self, phone, amount, reference, desc):
        token = self.get_token()
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode(f"{self.shortcode}{self.passkey}{timestamp}".encode()).decode()
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {
            'BusinessShortCode': self.shortcode,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': int(amount),
            'PartyA': phone,
            'PartyB': self.shortcode,
            'PhoneNumber': phone,
            'CallBackURL': f"{settings.BASE_URL}/payments/mpesa/callback/",
            'AccountReference': reference,
            'TransactionDesc': desc
        }
        r = requests.post(f'{self.base_url}/mpesa/stkpush/v1/processrequest', json=payload, headers=headers)
        res = r.json()
        if res.get('ResponseCode') == '0':
            return {'success': True, 'merchant_request_id': res['MerchantRequestID'], 'checkout_request_id': res['CheckoutRequestID']}
        return {'success': False, 'error': res.get('ResponseDescription', 'unknown')}

    def process_callback(self, data):
        try:
            body = data['Body']['stkCallback']
            result_code = body['ResultCode']
            merchant = body['MerchantRequestID']
            checkout = body['CheckoutRequestID']
            if result_code == 0:
                items = body['CallbackMetadata']['Item']
                metadata = {i['Name']: i.get('Value') for i in items}
                return {
                    'success': True,
                    'merchant_request_id': merchant,
                    'checkout_request_id': checkout,
                    'mpesa_receipt_number': metadata.get('MpesaReceiptNumber'),
                    'amount': metadata.get('Amount'),
                    'phone_number': metadata.get('PhoneNumber'),
                }
            else:
                return {'success': False, 'merchant_request_id': merchant, 'checkout_request_id': checkout, 'result_description': body.get('ResultDesc')}
        except Exception as e:
            logger.error(f"Callback error: {e}")
            return {'success': False, 'error': str(e)}