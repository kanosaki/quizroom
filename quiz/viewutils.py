from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse_lazy

from quiz.models import Participant


class SigninRequired(object):
    def __init__(self, fn, register_url=None):
        self.fn = fn
        self.register_url = register_url or reverse_lazy('participant_register')

    def __call__(self, req, *args, **kw):
        if 'uid' in req.session:
            user = Participant.objects.get(pk=req.session['uid'])
            return self.fn(req, user, *args, **kw)
        else:
            return HttpResponseRedirect(self.register_url)


signin_required = SigninRequired

