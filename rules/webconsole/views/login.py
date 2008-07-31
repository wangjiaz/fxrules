from django.http import HttpResponse
from django.template import Template, Context
from django.template.loader import get_template
from django.contrib import auth


def login_page(request):
  t = get_template('login.html')
  c = Context({})

  try:
    username = request.POST['username'].strip()
    password = request.POST['password'].strip()

    if username == '' or password == '':
      html = t.render(c)
      return HttpResponse(html)

    return HttpResponse (username)

  except Exception, ex:
    print ex
    html = t.render(c)
    return HttpResponse(html)
