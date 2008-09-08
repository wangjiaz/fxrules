from django.db import models

class Currency(models.Model):
  name = models.CharField (maxlength = 10, unique = True)
  count = models.IntegerField (default = 0)
  wincount = models.IntegerField (default = 0)

  def __str__ (self):
    return self.name

  class Admin:
    pass


rule_types = (
  ('buy', 'Buy'),
  ('sell', 'Sell'),
)

class Rule(models.Model):
  """ a set of check points """
  name = models.CharField(maxlength=100)
  createtime = models.DateTimeField(auto_now_add = True)
  count = models.IntegerField (default = 0)
  wincount = models.IntegerField (default = 0)
  type = models.CharField(maxlength = 10, choices = rule_types)
  inuse = models.BooleanField (default = True)
  memo = models.TextField (blank = 1)

  def __str__ (self):
    return self.name

  class Admin:
    pass


class Checkpoint (models.Model):
  """ a check point of a rule """
  description = models.TextField()
  rules = models.ManyToManyField (Rule)

  def __str__ (self):
    return self.description

  class Admin:
    pass


class Trade (models.Model):
  """ a buy/sell transaction """
  createtime = models.DateTimeField (auto_now_add = True)
  closetime = models.DateTimeField (auto_now = True)
  win = models.BooleanField(default = False)
  pts = models.IntegerField(default = 0)
  isover = models.BooleanField(default = False)
  memo = models.TextField(default='')

  m10 = models.URLField (null=True)
  h1 = models.URLField (null=True)
  h3 = models.URLField (null=True)
  d = models.URLField (null=True)

  rule = models.ForeignKey(Rule)
  currency = models.ForeignKey(Currency)

  def get_stats (count):
    """ get the stats for the last 'count' closed trades """
    trades = Trade.objects.filter(isover=True).order_by('-id')[:count]

    min_stop_lose, max_stop_lose = 10000, 0
    min_take_profit, max_take_profit = 10000, 0
    win_count = 0

    for t in trades:
      if t.win:
        win_count += 1
        if min_take_profit > t.pts:
          min_take_profit = t.pts
        if max_take_profit < t.pts:
          max_take_profit = t.pts

      else:
        if min_stop_lose > t.pts:
          min_stop_lose = t.pts
        if max_stop_lose < t.pts:
          max_stop_lose = t.pts

    win_ratio = win_count * 1.0 / count
    take_profit_range = (min_take_profit, max_take_profit)
    stop_lose_range = (-max_stop_lose, -min_stop_lose)

    return (count, win_ratio, take_profit_range, stop_lose_range)

  get_stats = staticmethod(get_stats)

  class Admin:
    pass


class Level (models.Model):
  """ record my current market value and the level I'm on """
  value = models.FloatField(max_digits=15, decimal_places=2)
  level = models.IntegerField(default=1)
  target = models.FloatField(max_digits=15, decimal_places=2)
  lastupdated = models.DateTimeField(auto_now = 1)


class Account (models.Model):
  """ account is the money management unit of my forex game """
  name = models.TextField (blank = True)
  balance = models.FloatField (max_digits = 15, decimal_places = 2)
  base = models.FloatField (max_digits = 15, decimal_places = 2)
  growth = models.FloatField (max_digits = 10, decimal_places = 5)
  strategy = models.TextField (blank = True)
  append_capital = models.BooleanField(default = False)

  level = models.IntegerField ()
  upgrade = models.FloatField (max_digits = 15, decimal_places = 2)
  downgrade = models.FloatField (max_digits = 15, decimal_places = 2)

  unit_ratio = models.FloatField (max_digits = 10, decimal_places = 5)
  unit = models.FloatField (max_digits = 15, decimal_places = 2)

  bonus_level = models.IntegerField()
  bonus_ratio = models.FloatField (max_digits = 10, decimal_places = 5)
  bonus_level_gap = models.IntegerField()
  bonus = models.FloatField (max_digits = 15, decimal_places = 2)
   
  lastupdated = models.DateTimeField(auto_now = 1)

  def __str__ (self):
    return '%s: %f' % (self.name, self.balance)

  def adjust (self):
    """ compute new information for this account """
    self.__level()
    self.__unit()

    if self.level >= self.bonus_level:
      notice = BonusNotice(account=self, amount=self.bonus)
      notice.save()

    self.__bonus()
    self.save()

    if self.append_capital:
      # have I reached the growth?
      if self.upgrade > self.balance >= self.downgrade * self.growth:
        notice = AppendCapitalNotice(account=self)
        notice.save()
      

  def validate(self):
    """ compute inferred vars from balance and fixed vars """

    self.__level()
    self.__unit()
    self.__bonus()

    self.save()

  def __level(self):
    n = 0
    a, b = 0.0, 0.0
    while True:
      if self.append_capital:
        a = self.base * (self.growth ** n - 1) / (self.growth - 1)
        b = a * self.growth + self.base
      else:
        a = self.base * self.growth ** (n-1)
        b = a * self.growth
      if b > self.balance:
        break
      n += 1

    self.level, self.downgrade, self.upgrade = n, a, b

  def __unit(self):
    unit = self.downgrade * self.unit_ratio
    self.unit = unit - unit % 10

  def __bonus(self):
    a, b = 0, self.bonus_level_gap
    while b <= self.level:
      a = b
      b = b + self.bonus_level_gap
    self.bonus_level = b

    down = 0.0
    if self.append_capital:
      down = self.base * (self.growth ** self.bonus_level - 1) / (self.growth - 1)
    else:
      down = self.base * self.growth ** (self.bonus_level - 1)
    self.bonus = down * self.bonus_ratio

  class Admin:
    pass


class AccountChange (models.Model):
  """ records account change history """
  account = models.ForeignKey (Account)
  delta = models.FloatField (max_digits = 15, decimal_places = 2)
  memo = models.TextField (blank = True)
  lastupdated = models.DateTimeField(auto_now = 1)

  class Admin:
    pass


class BonusNotice (models.Model):
  """ a piece of information telling me I have a bonus """
  account = models.ForeignKey (Account)
  amount = models.FloatField (max_digits = 15, decimal_places = 2)
  executed = models.BooleanField (default = False)
  memo = models.TextField (blank = True)
  lastupdated = models.DateTimeField(auto_now = 1)

  class Admin:
    pass


class AppendCapitalNotice(models.Model):
  """ let me know when to append capital to finish upgrade """
  account = models.ForeignKey (Account)
  executed = models.BooleanField (default = False)
  lastupdated = models.DateTimeField(auto_now = 1)

  class Admin:
    pass
