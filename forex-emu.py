import random
import sys, os

class Account (object):
  """ account is the money management unit of my forex game """

  def __init__ (self, base, append_capital, growth, unit_ratio, bonus_ratio, bonus_level_gap, name):
    self.base = base
    self.append_capital = append_capital
    self.growth = growth
    self.unit_ratio = unit_ratio
    self.bonus_ratio = bonus_ratio
    self.bonus_level_gap = bonus_level_gap
    self.name = name
    self.balance = self.base
    self.bonus_log = {}
    self.append_capital_log = {}

  def __str__ (self):
    return '%s: balance=%f, level=%d' % (self.name, self.balance, self.level)

  def adjust (self):
    """ compute new information for this account """
    result = (.0, .0)  # bonus, append_capital
    self.__level()
    self.__unit()

    take_bonus = (self.level >= self.bonus_level)
    if take_bonus:
      if not self.bonus_log.has_key(self.level):
        self.bonus_log[self.bonus_level] = 1.0
      r = random.Random()
      rval = r.random()
      if rval < self.bonus_log[self.bonus_level]:
        result = (self.bonus, 0.0)
        self.bonus_log[self.bonus_level] /= 4

    self.__bonus()

    if self.append_capital:
      # have I reached the growth?
      if self.level >= 1 and self.upgrade > self.balance >= self.downgrade * self.growth:
        if not self.append_capital_log.has_key(self.level):
          result = (result[0], self.base)
          self.append_capital_log[self.level] = self.base

    return result
      
  def validate(self):
    """ compute inferred vars from balance and fixed vars """

    self.__level()
    self.__unit()
    self.__bonus()

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


class Trade (object):
  """ A trade represents an forex transaction. """

  win_ratio = 0.75
  stop_lose_range = range(15, 21)
  take_profit_range = range(20, 41)

  def __init__ (self, unit):
    """ init a new trade with the given unit capital """
    self.unit = unit
    self.executed = False

  def execute (self):
    """ execute this trade and get result """
    r = random.Random()
    rval = r.random()
    self.is_win = rval >= (1 - self.win_ratio)

    self.pips = 0
    if self.is_win == True:
      self.pips = r.choice(self.take_profit_range)
    else:
      self.pips = - r.choice(self.stop_lose_range)
    self.delta = self.unit / 100.0 * self.pips

    self.executed = True


  def __str__ (self):
    if not self.executed:
      return 'Trade with %f, not executed' % (self.unit)
    else:
      s = 'win'
      if not self.is_win:
        s = 'lose'

      return 'trade with %f, %s, pips: %d, profit: %f' % (self.unit, s, self.pips, self.delta)


class Sequence (object):
  """ A sequence emulates a set of trades. """

  def __init__ (self, stop_value, system_a_value=500.0, system_b_value=20.0):
    self.system_a = Account(base=500, append_capital=True, growth=1.1, unit_ratio=0.0625, bonus_ratio=0.05, bonus_level_gap=5, name='system A')
    self.system_b = Account(base=20, append_capital=False, growth=1.67, unit_ratio=1, bonus_ratio=0.2, bonus_level_gap=1, name='system B')

    self.stop_value = stop_value

    self.system_a.balance = system_a_value
    self.system_b.balance = system_b_value

    self.system_a.validate()
    self.system_b.validate()

    self.final_status = 0 # 0 means win, 1 means lose
    self.pips_win, self.pips_lose = 0, 0

    self.total_bonus_system_a = .0
    self.total_bonus_system_b = .0
    self.total_bonus = .0

  def run (self):
    self.round = 1
    while self.system_a.balance >= 10.00 and self.system_b.balance >= 10.00 and self.system_a.balance + self.system_b.balance < self.stop_value:
      print 'trade round: %d' % (self.round)
      print ' ', self.system_a, '; ', self.system_b, '; total balance: %f' % (self.system_a.balance + self.system_b.balance)

      unit = self.system_a.unit + self.system_b.unit
      print '  capital from system a: %f, capital from system b: %f' % (self.system_a.unit, self.system_b.unit)
      t = Trade(unit)
      t.execute()
      print ' ', t
      
      if t.is_win: self.pips_win += t.pips
      else: self.pips_lose += t.pips

      r = self.system_a.unit / unit
      delta_a = t.delta * r
      print '  system a change: %f, system b change: %f' % (delta_a, t.delta - delta_a)

      self.system_a.balance += delta_a
      self.system_b.balance += t.delta - delta_a

      result_b = self.system_b.adjust()
      if result_b[0] > 0: 
        # take bonus from system b
        b = self.system_b.bonus
        print '  take bonus from system b: %f' % (b)

        half_b = b/2
        self.system_a.balance += half_b
        print '  move %f to system a' % (half_b)

        self.total_bonus_system_b += half_b
        self.total_bonus += half_b
        print '  taking %f from system b as bonus' % (half_b)

        self.system_b.balance -= b
        self.system_b.adjust()

      result_a = self.system_a.adjust()
      if result_a[1] > 0:
        print '  system a notify me to append capital %f' % (self.system_a.base)
        self.system_a.balance += self.system_a.base
        result_a = self.system_a.adjust()

      if result_a[0] > 0:
        print '  take bonus from system a: %f' % (self.system_a.bonus)
        self.system_a.balance -= self.system_a.bonus
        self.system_a.adjust()
        self.total_bonus_system_a += self.system_a.bonus
        self.total_bonus += self.system_a.bonus

      print '  closing state: ', self.system_a, '; ', self.system_b
      print '  total balance: %f' % (self.system_a.balance + self.system_b.balance)

      self.round += 1

    if self.system_a.balance < 10:
      self.final_status = 1
      print 'system a game over'
      return 

    if self.system_b.balance < 10:
      self.final_status = 1
      print 'system b game over'
      return

    print 'win the game in %d rounds, pips won: %d, pips lost: %d; bonus: %f' % (self.round, self.pips_win, self.pips_lose, self.total_bonus)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    print 'usage: python forex-emu.py <stop balance>'
    sys.exit(0)

  stop_value = float(sys.argv[1])
  
  n = 30 # emulate 30 times and take average
  rounds = n # used for compute avg values
  n_win, n_lose = 0, 0
  n_win_rounds = 0
  pips_won, pips_lost = 0, 0
  bonus = .0
  while n > 0:
    n -= 1
    s = Sequence(stop_value, 461.84, 18.3)
    s.run()
    if s.final_status == 0:
      n_win += 1
      n_win_rounds += s.round
    else:
      n_lose += 1

    pips_won += s.pips_win
    pips_lost += s.pips_lose
    bonus += s.total_bonus

  print 'final stats for reaching %f' % (stop_value)

  avg_win_rounds = n_win_rounds * 1.0 / n_win
  avg_pips_won = pips_won * 1.0 / rounds
  avg_pips_lost = pips_lost * 1.0 / rounds
  avg_bonus = bonus / rounds
  
  print '  win: %d, lose: %d; avg win rounds: %f; avg pips won: %f, avg pips lost: %f; avg bonus: %f' % (n_win, n_lose, avg_win_rounds, avg_pips_won, avg_pips_lost, avg_bonus)
