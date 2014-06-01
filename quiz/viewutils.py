from django.http import HttpRequest, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy


class SigninRequired(object):
    signup_url = reverse_lazy('user_signup')

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, req: HttpRequest, *args, **kw):
        if 'uid' in req.session:
            return self.fn(req, *args, **kw)
        else:
            return HttpResponseRedirect(self.signup_url)


signin_required = SigninRequired
