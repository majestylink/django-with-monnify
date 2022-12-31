import hmac
import json

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView

from core.models import Book, OrderPayment
from core.serializers import BookSerializer
from core.utils import MonnifyClient, ApiResponse, error_to_string
from testDjangoProject import settings

monnify = MonnifyClient(settings.BS4_SECRET_KEY)


class Index(APIView):
    serializer_class = BookSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return ApiResponse(
                message=error_to_string(serializer.errors), data=serializer.errors, status_code=400
            ).response()
        book = Book.objects.get(id=request.data['id'])
        data = self.serializer_class(instance=book).data
        monnify.login()
        data["checkourl_url"] = monnify.generate_checkout_url(book.id, request.user)
        return ApiResponse(200, data=data).response()


def compute_hash(request_body, monnify_signature):
    import hashlib
    sk = settings.MONNIFY_SECRET_KEY
    sign = hmac.new(sk.encode(), request_body.decode("utf-8").encode(), hashlib.sha512).hexdigest()
    if sign != monnify_signature:
        return False
    return True


@csrf_exempt
def transaction_completed(request):
    if request.method == 'POST':
        if compute_hash(request.body, request.headers.get('Monnify-Signature', None)):
            eventData = json.loads(request.body)['eventData']
            try:
                user = None
                if eventData['paymentStatus'] == 'PAID':
                    op = OrderPayment.objects.create(
                        book=Book.objects.get(id=int(eventData['paymentReference'].split('|')[0])),
                        user=User.objects.get(email=eventData['customer']['email'])
                    )
            except:
                return HttpResponse("Invalid Response")

    return HttpResponse("Webhook received!")
