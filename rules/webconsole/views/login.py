from django.http import *
from django.template import Template, Context
from django.template.loader import get_template
from django.contrib import auth


def login(request):
  t = get_template('login.html')
  c = Context({})

  try:
    username = request.POST['username'].strip()
    password = request.POST['password'].strip()

    if username == '' or password == '':
      html = t.render(c)
      return HttpResponse(html)
    else:
      user = auth.authenticate(username=username, password=password)
      if user is not None:
        auth.login (request, user)
        return HttpResponseRedirect('/home')
      else:
        c['message'] = 'username or password incorrect'
        html = t.render(c)
        return HttpResponse(html)

  except Exception, ex:
    print ex
    html = t.render(c)
    return HttpResponse(html)
