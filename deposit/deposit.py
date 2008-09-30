# deposit.py
#   compute the strategy to get interest from fixed duration deposit
#
# 2008/09/30, create

import datetime
import logging

logging.basicConfig (level=logging.DEBUG, 
    format='%(asctime)s %(levelname)s %(message)s')

class Unit (object):
  """ a unit is the object I monthly deposit into bank account """

  def __init__ (self, principle, duration, rate, taxrate, start):
    self.principle = float(principle)
    self.duration = int(duration) # delta in month
    self.rate = float(rate)
    self.taxrate = float(taxrate)
    self.start = start

    self.next_duedate = self.start
    self.amount = self.principle

    self.due_date()

  def due_date (self):
    m = self.next_duedate.month + self.duration
    if m <= 12:
      self.next_duedate = self.next_duedate.replace(month=m)
    else:
      y = self.next_duedate.year
      while m > 12:
        y += 1 
        m -= 12
      self.next_duedate = self.next_duedate.replace(year=y, month=m)

  def grow (self, end):
    """ compute the unit amount till the end date """
    while self.next_duedate <= end:
      interest = self.amount * self.rate * self.duration / 12 * (1-self.taxrate)
      self.amount += interest
      self.due_date()

  def __str__ (self):
    s = 'amount: %f; growth: %f; (%d m)' % (self.amount, self.amount / self.principle, self.duration)
    return s


class LiveDemo (object):
  """ demo my deposit strategy execution """

  def __init__ (self, start, end, principle, duration, rate, tax):
    self.start = start
    self.end = end
    self.units = []

    self.principle = principle
    self.duration = duration
    self.rate = rate
    self.tax = tax

    self.total_principle = 0.0

  def run (self):
    """ deposit once a month till end, let's see the result """
    today = self.start

    while today <= self.end:
      u = Unit(self.principle, self.duration, self.rate,
          self.tax, today)
      self.units.append(u)
      self.total_principle += self.principle

      for x in self.units:
        x.grow(today)

      m = today.month + 1
      y = today.year

      if m <= 12: today = today.replace(month=m)
      else: today = today.replace(year = y+1, month = m-12)

    self.sum = .0
    for u in self.units:
      self.sum += u.amount
    print 'from %s to %s, %d month, total=%f, total principle=%f' % (self.start, self.end, self.duration, self.sum, self.total_principle)


def growth_compare ():
  start = datetime.date(2008, 9, 30)
  end = datetime.date(2030, 8, 1)

  u3 = Unit(5000, 3, 0.0333, 0.05, start)
  u6 = Unit(5000, 6, 0.0378, 0.05, start)
  u12 = Unit(5000, 12, 0.0414, 0.05, start)
  u24 = Unit(5000, 24, 0.0468, 0.05, start)
  u36 = Unit(5000, 36, 0.054, 0.05, start)
  u60 = Unit(5000, 60, 0.0585, 0.05, start)

  for u in [u3, u6, u12, u24, u36, u60]:
    u.grow(end)
    print u


def strategy_compare ():
  start = datetime.date(2008, 10, 15)
  end = datetime.date(2030, 10, 15)

  d3 = LiveDemo (start, end, 5000, 3, 0.0333, 0.05)
  d6 = LiveDemo (start, end, 5000, 6, 0.0378, 0.05)
  d12 = LiveDemo (start, end, 5000, 12, 0.0414, 0.05)
  d24 = LiveDemo (start, end, 5000, 24, 0.0468, 0.05)
  d36 = LiveDemo (start, end, 5000, 36, 0.0540, 0.05)
  d60 = LiveDemo (start, end, 5000, 60, 0.0585, 0.05)

  for d in [d3, d6, d12, d24, d36, d60]:
    d.run()

if __name__ == '__main__':
  strategy_compare()
