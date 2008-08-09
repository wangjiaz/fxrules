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

  rule = models.ForeignKey(Rule)
  currency = models.ForeignKey(Currency)

  class Admin:
    pass


class Level (models.Model):
  """ record my current market value and the level I'm on """
  value = models.FloatField(max_digits=15, decimal_places=2)
  level = models.IntegerField(default=1)
  target = models.FloatField(max_digits=15, decimal_places=2)
  lastupdated = models.DateTimeField(auto_now = 1)
