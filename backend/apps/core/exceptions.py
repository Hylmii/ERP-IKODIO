"""
Custom exception handler for API responses
"""
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats error responses consistently
    """
    response = exception_handler(exc, context)

    if response is not None:
        custom_response_data = {
            'success': False,
            'error': {
                'message': '',
                'details': {}
            }
        }

        if isinstance(exc, ValidationError):
            custom_response_data['error']['message'] = 'Validation error'
            custom_response_data['error']['details'] = response.data
        else:
            if isinstance(response.data, dict):
                custom_response_data['error']['message'] = response.data.get(
                    'detail', 
                    str(exc)
                )
                custom_response_data['error']['details'] = response.data
            else:
                custom_response_data['error']['message'] = str(exc)

        response.data = custom_response_data

    return response
