from django.http import *
from django.template import Template, Context
from django.template.loader import get_template
from django.contrib import auth
from rules.webconsole.models import *
from django.shortcuts import render_to_response

class globalstat:
  pass

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

  trades = Trade.objects.filter(isover = False).order_by('-id')

  # global stats
  st = globalstat()
  st.count = Trade.objects.count()
  st.wincount = Trade.objects.filter(win = True).count()
  if st.count > 0: st.win_ratio = st.wincount * 100.0 / st.count
  else: st.win_ratio = 0.0

  currencies = Currency.objects.all()
  for c in currencies:
    if c.count == 0: c.win_ratio = 0.0
    else: c.win_ratio = c.wincount * 100.0 / c.count

  # get accounts data
  accounts = Account.objects.all().order_by('id')
  balance = 0.0
  unit = 0
  for x in accounts:
    balance += x.balance
    unit += x.unit
    if x.balance > 0:
      if x.unit == 0:
        x.up_ratio = x.upgrade / x.balance
        x.down_ratio = x.downgrade / x.balance
      else:
        x.up_ratio = (x.upgrade - x.balance) / x.unit
        x.down_ratio = (x.balance - x.downgrade) / x.unit

    x.bonus_notices = x.bonusnotice_set.filter(executed = False).order_by('-id')

    if x.append_capital:
      x.append_notices = x.appendcapitalnotice_set.filter(executed = False).order_by('-id')


  # get trades stats
  stat_8 = Trade.get_stats(8)
  stat_16 = Trade.get_stats(16)

  values = { 'buy_rules': buy_rules,
      'sell_rules': sell_rules,
      'n_buy_rules': n_buy_rules,
      'n_sell_rules': n_sell_rules, 
      'trades': trades,
      'user': request.user,
      'stat': st,
      'currencies': currencies,
      'balance': balance,
      'unit': unit,
      'accounts': accounts,
      'stat_8': stat_8,
      'stat_16': stat_16,
  }

  return render_to_response ('home.html', values)


def newtrade (request, ruleid):
  """ return a page for submnit a new trade """

  rule = Rule.objects.get(id=ruleid)

  if request.method == 'POST':
    currency_name = request.POST.get('currency', '')
    c = Currency.objects.get(name=currency_name)

    memo = request.POST.get('memo', '')

    # create new trade
    trade = Trade()
    trade.rule = rule
    trade.currency = c
    trade.memo = memo
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
      'user': request.user,
  }

  return render_to_response ('newtrade.html', values)


def closetrade (request, tradeid):
  """ close a trade and record result """

  trade = Trade.objects.get(id = tradeid)

  if request.method == 'POST':
    pts = request.POST.get ('pts', 0)
    iswin = request.POST.get ('win', True)
    iswin = int(iswin)
    memo = request.POST['memo']

    trade.isover = True
    trade.win = bool(iswin)
    trade.pts = int(pts)
    trade.memo = memo
    trade.save()

    # update wincount
    if trade.win:
      trade.rule.wincount += 1
      trade.rule.save()
      trade.currency.wincount += 1
      trade.currency.save()

    return HttpResponse('')

  else:
    values = {'trade': trade,
      'user': request.user,
    }

    return render_to_response ('closetrade.html', values)

def rulestat (request, ruleid):
  rule = Rule.objects.get(id=ruleid)
  trades = rule.trade_set.all().order_by('-id')
  n_trades = len(trades)
  checkpoints = rule.checkpoint_set.all()

  # compute win_ratio for this rule
  if rule.count == 0:
    rule.win_ratio = 0.0
  else:
    rule.win_ratio = rule.wincount * 100.0 / rule.count

  # compute performance for each currency
  currency_stat = {}
  for t in trades:
    if not currency_stat.has_key(t.currency.id):
      currency_stat[t.currency.id] = (0, 0)

    a, b = currency_stat[t.currency.id]
    b += 1

    if t.win: a += 1
    currency_stat[t.currency.id] = (a, b)

  for k, v in currency_stat.items():
    win_ratio = 0.0
    if v[1] > 0:
      win_ratio = v[0] * 100.0 / v[1]
    currency_stat[k] = (v[0], v[1], win_ratio)

  currencies = []
  for k in currency_stat.keys():
    c = Currency.objects.get(id=k)
    currencies.append(c)
    c.wincount, c.count, c.win_ratio = currency_stat[k]

  # change \n to <br/> for trade memo
  for t in trades:
    t.memo = t.memo.replace('\n', '<br/>')

  values = {'rule': rule,
      'trades': trades,
      'n_trades': n_trades,
      'currencies': currencies,
      'user': request.user,
      'checkpoints': checkpoints,
  }

  return render_to_response('rule.html', values)


def savevalue (request): 
  """ save a new value and compute its level """
  v = request.POST['newvalue']
  level = Level()
  level.value = float(v)

  # compute current level and target value, with base=500$ and growth rate = 1.1
  n = 1
  base = 500
  rate = 1.1
  target = base * rate
  while level.value > target:
    n += 1
    target = (target + base) * rate

  level.level = n
  level.target = target

  Level.save(level)

  return HttpResponseRedirect('/home')

def savedelta(request, accountid):

  delta, memo = None, None

  try:
    delta = request.POST.get('delta', 0.0)
    delta = float(delta)
    memo = request.POST.get('memo', '')
  except:
    delta = 0.0

  # update account
  account = Account.objects.get(id=accountid)
  account.balance += delta
  account.adjust()

  # create a new change log
  change = AccountChange(delta = delta, memo = memo)
  change.account = account
  change.save()

  return HttpResponseRedirect('/home')

def validateaccount(request, accountid):
  account = Account.objects.get(id=accountid)
  account.validate()
  return HttpResponseRedirect('/home')

def executeappend(request, noticeid):
  notice = AppendCapitalNotice.objects.get(id=noticeid)
  notice.executed = True
  notice.save()
  return HttpResponseRedirect('/home')

def takebonus(request, bonusid):
  bonus = BonusNotice.objects.get(id=bonusid)
  bonus.account.balance -= bonus.amount
  bonus.account.validate()
  bonus.executed = True
  bonus.save()
  return HttpResponseRedirect('/home')

def skipbonus(request, bonusid):
  bonus = BonusNotice.objects.get(id=bonusid)
  bonus.executed = True
  bonus.save()
  return HttpResponseRedirect('/home')

def tradelist(request, page):

  win = request.GET.get('result', 'all')

  # compute offset and limit
  p = int(page)
  per_page = 10
  start = (p - 1) * per_page
  end = start + per_page

  count = 0
  trades = None

  if win == 'win':
    count = Trade.objects.filter(win=True).count()
    trades = Trade.objects.filter(win=True).order_by('-createtime')[start:end]
  elif win == 'lose':
    count = Trade.objects.filter(win=False).count()
    trades = Trade.objects.filter(win=False).order_by('-createtime')[start:end]
  else:
    count = Trade.objects.count()
    trades = Trade.objects.all().order_by('-createtime')[start:end]

  # compute pages navigation
  pages = (count-1)  / per_page
  pages += 1
  pagelist = range(1, pages + 1)

  for t in trades:
    t.memo = t.memo.replace ('\n', '<br/>')

  # compute time thread
  far = Trade.objects.all().order_by('id')[:1][0]
  near = Trade.objects.all().order_by('-id')[:1][0]
  tm_far = far.createtime
  tm_near = near.createtime
  y, m = tm_near.year, tm_near.month
  tm_thread = []

  while y > tm_far.year or m >= tm_far.month:
    tm_thread.append ((y, m))
    m -= 1
    if m == 0:
      m = 12
      y -= 1

  values = {
      'trades': trades,
      'pagelist': pagelist,
      'page': page,
      'user': request.user,
      'result': win,
      'calendar': tm_thread,
    }

  return render_to_response ('tradelist.html', values)


def trade(request, tradeid):
  trade = Trade.objects.get(id=tradeid)

  values = {
      'trade': trade,
      'user': request.user,
      }

  return render_to_response ('trade.html', values)


def updatetrade(request, tradeid):
  trade = Trade.objects.get(id=tradeid)
  
  m10 = request.POST.get('m10', None)
  h1 = request.POST.get('h1', None)
  h3 = request.POST.get('h3', None)
  d = request.POST.get('d', None)
  memo = request.POST.get('memo', '')

  trade.m10 = m10
  trade.h1 = h1
  trade.h3 = h3
  trade.d = d
  trade.memo = memo

  try:
    pts = request.POST.get('pts')
    trade.pts = int(pts)
  except:
    pass

  trade.save()

  return HttpResponseRedirect('/trade/%d/' % (trade.id))

