from django.http import *
from django.template import Template, Context
from django.template.loader import get_template
from django.contrib import auth
from rules.webconsole.models import *
from rules.webconsole.forms import *
from django.shortcuts import render_to_response

def home(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/login/')

  else:
    c = Context()
    t = get_template('home.html')
    return HttpResponse(t.render(c))


def createrule(request):
  """ show the page for creating a new rule """
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/login/')

  if request.method == 'POST':
    form = RuleForm(request.POST)
  else:
    form = RuleForm()

  return render_to_response('createrule.html', {'form': form})
