import datetime
import json
import time

from django.contrib.sites import requests
from rest_framework import status
from rest_framework.response import Response

from core.models import Book


class MonnifyClient:
    def __init__(self, bs4_secret_key: str):
        self.bs4_secret_key = bs4_secret_key
        self.access_token = None

    def login(self):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Basic " + self.bs4_secret_key
        }
        base_url = 'https://sandbox.monnify.com/api/v1/auth/login'
        response = requests.post(f"{base_url}", headers=headers)
        self.access_token = response.json()['responseBody']['accessToken']

    def generate_checkout_url(self, book_id, user):
        try:
            book = Book.objects.get(id=book_id)
        except:
            return None
        try:
            data = {
                "amount": 1000,
                "customerName": user.email.split('@')[0],
                "customerEmail": user.email,
                "paymentReference": str(book.id) + '|' + str(int(time.mktime(datetime.datetime.now().timetuple()))),
                "paymentDescription": "Book Order",
                "currencyCode": "NGN",
                "contractCode": "8418534685",
                "redirectUrl": "https://en.wikipedia.org/wiki/ISBN",
                "paymentMethods": ["CARD", "ACCOUNT_TRANSFER"]
            }
            BASE_URL = 'https://sandbox.monnify.com/api/v1/merchant/transactions/init-transaction'
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + self.access_token
            }
            response = requests.post(f"{BASE_URL}", data=json.dumps(data), headers=headers)

            if response.json()['requestSuccessful']:
                return response.json()['responseBody']['checkoutUrl']
        except:
            return None


class ApiResponse:
    STATUS_MAPPING = {
        200: (True, None),
        201: (True, status.HTTP_201_CREATED),
        400: (False, status.HTTP_400_BAD_REQUEST),
        403: (False, status.HTTP_403_FORBIDDEN),
        404: (False, status.HTTP_404_NOT_FOUND)
    }

    def __init__(self, status_code=200, message=None, data=None):
        self.message = message
        self.data = data
        self.status_code = status_code

    def _fetch_status(self):
        return self.STATUS_MAPPING[self.status_code]

    def response(self):
        status, status_code = self._fetch_status()
        response_data = {"status": status, "message": None, "data": None}
        if self.message:
            response_data['message'] = self.message
        if self.data or self.data == []:
            response_data['data'] = self.data
        return Response(response_data, status_code)


def error_to_string(error: dict):
    try:
        first_value = list(error.values())[0]
        if type(first_value) == str:
            return first_value
        elif type(first_value) == list:
            return first_value[0]
        else:
            return first_value
    except:
        pass
    return "There seems to be An Error with your request. Please try again"
