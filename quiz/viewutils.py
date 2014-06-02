from django.http import HttpRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy

from quiz.models import Participant


class SigninRequired(object):
    signup_url = reverse_lazy('user_signup')

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, req, *args, **kw):
        if 'uid' in req.session:
            user = Participant.objects.get(pk=req.session['uid'])
            return self.fn(req, user, *args, **kw)
        else:
            return HttpResponseRedirect(self.signup_url)


signin_required = SigninRequired
