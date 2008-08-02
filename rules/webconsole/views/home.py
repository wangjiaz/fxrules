from django.http import *
from django.template import Template, Context
from django.template.loader import get_template
from django.contrib import auth
from rules.webconsole.models import *
from django.shortcuts import render_to_response

def home(request):
  if not request.user.is_authenticated():
    return HttpResponseRedirect('/login/')

  rules = Rule.objects.all()
  buy_rules, sell_rules = [], []

  # filter rules to buy/sell and compute win_ratio
  for rule in rules:
    if rule.count == 0:
      rule.win_ratio = 0
    else:
      rule.win_ratio = rule.wincount * 100.0 / rule.count

    if rule.type == 'buy':
      buy_rules.append(rule)
    else:
      sell_rules.append(rule)

  n_buy_rules = len(buy_rules)
  n_sell_rules = len(sell_rules)

  values = { 'buy_rules': buy_rules,
      'sell_rules': sell_rules,
      'n_buy_rules': n_buy_rules,
      'n_sell_rules': n_sell_rules, 
  }

  return render_to_response ('home.html', values)


def newtrade (request, ruleid):
  """ return a page for submnit a new trade """

  rule = Rule.objects.get(id=ruleid)

  if request.method == 'POST':
    currency_name = request.POST.get('currency', '')
    c = Currency.objects.get(name=currency_name)

    # create new trade
    trade = Trade()
    trade.rule = rule
    trade.currency = c
    trade.save()

    # up count
    rule.count += 1
    rule.save()
    c.count += 1
    c.save()

    return HttpResponseRedirect('/home')

  checkpoints = rule.checkpoint_set.all()
  currencies = Currency.objects.all()

  # compute win_ratio
  if rule.count == 0:
    rule.win_ratio = 0.0
  else:
    rule.win_ratio = rule.wincount * 100.0 / rule.count

  values = {'rule': rule,
      'currencies': currencies,
      'checkpoints': checkpoints,
  }

  return render_to_response ('newtrade.html', values)
