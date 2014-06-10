import json
import traceback

from django.http import HttpResponse


class JsonResponse(HttpResponse):
    def __init__(self, content={}, mimetype=None, status=None,
                 content_type='application/json'):
        super(JsonResponse, self).__init__(json.dumps(content), mimetype=mimetype,
                                           status=status, content_type=content_type)

    # For testing
    def deserialize(self):
        return self.content.decode('ascii')


class JsonStatuses(object):
    @staticmethod
    def ok(**kw):
        kw.update(status='ok')
        return JsonResponse(kw)

    @staticmethod
    def failed(msg, **kw):
        kw.update(status='failed', message=msg)
        return JsonResponse(kw)


def json_api(f):
    def wrapper(*args, **kw):
        try:
            return JsonStatuses.ok(data=f(*args, **kw))
        except Exception as e:
            traceback.print_exc()
            return JsonStatuses.failed(e)
    return wrapper


def api_guard(f):
    def wrapper(*args, **kw):
        try:
            return f(*args, **kw)
        except Exception as e:
            traceback.print_exc()
            return HttpResponse(unicode(e))
    return wrapper