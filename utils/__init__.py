import json

from django.http import HttpResponse


class JsonResponse(HttpResponse):
    def __init__(self, content={}, mimetype=None, status=None,
                 content_type='application/json'):
        super(JsonResponse, self).__init__(json.dumps(content), mimetype=mimetype,
                                           status=status, content_type=content_type)


class JsonStatuses(object):
    @staticmethod
    def ok():
        return JsonResponse({'status': 'ok'})

    @staticmethod
    def failed(msg):
        return JsonResponse({
            'status': 'failed',
            'message': msg,
        })

