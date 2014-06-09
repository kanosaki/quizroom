import json

from django.http import HttpResponse


class JsonResponse(HttpResponse):
    def __init__(self, content={}, mimetype=None, status=None,
                 content_type='application/json'):
        super(JsonResponse, self).__init__(json.dumps(content), mimetype=mimetype,
                                           status=status, content_type=content_type)


class JsonStatuses(object):
    @staticmethod
    def ok(data=None):
        data = data or {}
        data.update(status='ok')
        return JsonResponse(data)

    @staticmethod
    def failed(msg):
        return JsonResponse({
            'status': 'failed',
            'message': unicode(msg),
        })


def json_api(f):
    def wrapper(*args, **kw):
        try:
            return JsonStatuses.ok(f(*args, **kw))
        except Exception, e:
            return JsonStatuses.failed(e)
    return wrapper
