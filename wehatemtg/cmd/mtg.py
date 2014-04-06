#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import curses
import time
from decimal import Decimal, ROUND_DOWN
from abc import ABCMeta, abstractmethod
import signal
import sys

from pyfiglet import Figlet

DEFAULT_CURRENCY = 'JPY'
DEFAULT_HOURS_WORKED_PER_DAY = 8
DEFAULT_DAYS_WORKED_PER_MONTH = 20
DEFAULT_NUMBER_OF_PARTICIPANTS = 1


class Currencies(object):
    support_currencies = {
        'JPY': {
            'rate': 10000,
            'point': 0,
            'salary': 408,
        },
        'USD': {
            'rate': 1000000,
            'point': 2,
            'salary': 4.08,
        },
    }

    @classmethod
    def support(cls, currency):
        return currency.upper() in cls.support_currencies

    @classmethod
    def rate(cls, currency):
        return cls._currency_profile(currency, 'rate')

    @classmethod
    def point(cls, currency):
        return cls._currency_profile(currency, 'point')

    @classmethod
    def salary(cls, currency):
        return cls._currency_profile(currency, 'salary')

    @classmethod
    def _currency_profile(cls, currency, profile):
        currency = currency.upper()

        if not cls.support(currency):
            raise ValueError('{0} is not supported'.format(currency))

        return cls.support_currencies[currency][profile]


def floor_decimal(dec, point=0):
    point = '0' * point
    quantize_format = Decimal('1.{0}'.format(point))
    return dec.quantize(quantize_format, rounding=ROUND_DOWN)


class CostIntegrator(object):

    def __init__(self, salary_params=None):
        shortened_annual_salary = salary_params.get(
            'annual_salary'
        )
        self.currency = salary_params.get(
            'currency',
        )
        hours_worked_per_day = salary_params.get(
            'hours_worked_per_day',
        )
        days_worked_per_month = salary_params.get(
            'days_worked_per_month',
        )
        self.number_of_participants = salary_params.get(
            'number_of_participants',
        )

        # 通貨毎の短縮率 (JPY だと 10k, USD だと 1M 単位で入力される)
        currency_rate = Currencies.rate(self.currency)
        # 短縮されていない年収に戻す
        annual_salary = Decimal(shortened_annual_salary) * currency_rate
        # 一月当たりの労働時間 (hours)
        hours_worked_per_month = hours_worked_per_day * days_worked_per_month
        # 一年当たりの労働時間 (seconds)
        seconds_worked_per_year = 12 * hours_worked_per_month * 3600
        # 一秒当たりの給与
        self.salary_per_second = annual_salary / seconds_worked_per_year

        # 使われた給与
        self.total = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.total += self.salary_per_second * self.number_of_participants
        return self.total

    def next(self):
        return self.__next__()


class PeriodicScreen(object):

    __metaclass__ = ABCMeta

    def __init__(self, refresh_interval=1):
        self.refresh_interval = refresh_interval
        self.stdscr = curses.initscr()
        self.stdscr.keypad(1)
        curses.noecho()
        curses.cbreak()
        signal.signal(signal.SIGHUP, self.end)

    @abstractmethod
    def show(self):
        pass

    def start(self):
        try:
            while True:
                data = self.show()
                self.stdscr.addstr(0, 0, '{0}'.format(data))
                self.stdscr.refresh()
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.end()
            print(data)

    def end(self):
        curses.nocbreak()
        curses.echo()
        self.stdscr.keypad(0)
        curses.endwin()


def separate_comma_per_3digits(n):
    str_n = str(n)

    # 小数点以下を含むか
    point_index = str_n.rfind('.')
    if point_index != -1:
        # 含むならカンマを付ける範囲を絞る
        range_boundary = point_index
        # 小数点以下の部分を取り出しておく
        point = str_n[range_boundary:]
    else:
        # 含まないなら最後まで
        range_boundary = len(str_n)
        # 小数点以下はなし
        point = ''

    # カンマを打つ位置 (3 桁毎) の位置を取り出す
    separate_positions = range(range_boundary, 0, -3) + [0]
    # スライスで切り出す範囲をタプルにする
    separate_tuple_positions = [
        (separate_positions[i], separate_positions[i + 1])
        for i in range(len(separate_positions) - 1)
    ]
    # 文字列を 3 桁毎に切り出して配列にする
    str_n_pieces = [
        str_n[start:end]
        for end, start in separate_tuple_positions
    ]
    str_n_pieces.reverse()
    # カンマを挿入して小数点を付与する
    return ','.join(str_n_pieces) + point


class CostsScreen(PeriodicScreen):

    def __init__(self, integrator):
        super(CostsScreen, self).__init__()
        self.integrator = integrator

    def show(self):
        costs = next(self.integrator)
        point = Currencies.point(self.integrator.currency)
        normalized_costs = floor_decimal(costs, point)
        separated_costs = separate_comma_per_3digits(normalized_costs)
        return '{0} {1}'.format(separated_costs, self.integrator.currency)


class DecoratedCostsScreen(CostsScreen):

    def __init__(self, integrator, font='big'):
        super(CostsScreen, self).__init__()
        self.integrator = integrator
        self.fighler = Figlet(font=font)

    def show(self):
        data = super(DecoratedCostsScreen, self).show()
        return self.fighler.renderText(data)


def _execute(args):
    salary_params = {
        'annual_salary': args.annual_salary,
        'currency': args.currency,
        'hours_worked_per_day': args.hours_worked_per_day,
        'days_worked_per_month': args.days_worked_per_month,
        'number_of_participants': args.number_of_participants,
    }
    integrator = CostIntegrator(salary_params)
    screen = DecoratedCostsScreen(integrator)
    screen.start()


def _invalid_argument(arg_params):
    reason = 'error: the following argument is invalid'
    _invalid(arg_params, reason)


def _invalid(entry, reason):
    msg = '%s: %s: %s' % (sys.argv[0], reason, entry)
    raise ValueError(msg)


def _validate(args):
    if not Currencies.support(args.currency):
        _invalid_argument('-c/--currency')


def _post_processing(args):
    if args.annual_salary is None:
        args.annual_salary = Currencies.salary(args.currency)


def _parse_args():
    description = 'We hate meeting'
    arg_parser = argparse.ArgumentParser(description=description)

    option_s_help = 'Member\'s average annual salary'
    '(shortest, JPY:10k, USD:1M)'
    arg_parser.add_argument(
        '-s', '--annual-salary',
        type=float,
        required=False, default=None,
        help=option_s_help,
    )

    option_c_help = 'Currency (e.g. JPY, USD)'
    arg_parser.add_argument(
        '-c', '--currency',
        type=str,
        required=False, default=DEFAULT_CURRENCY,
        help=option_c_help,
    )

    option_t_help = 'Member\'s average hours worked per day'
    arg_parser.add_argument(
        '-t', '--hours-worked-per-day',
        type=int,
        required=False, default=DEFAULT_HOURS_WORKED_PER_DAY,
        help=option_t_help,
    )

    option_d_help = 'Member\'s average days worked per month'
    arg_parser.add_argument(
        '-d', '--days-worked-per-month',
        type=int,
        required=False, default=DEFAULT_DAYS_WORKED_PER_MONTH,
        help=option_d_help,
    )

    option_d_help = 'The number of participants of the meeting'
    arg_parser.add_argument(
        '-n', '--number-of-participants',
        type=int,
        required=False, default=DEFAULT_NUMBER_OF_PARTICIPANTS,
        help=option_d_help,
    )

    args = arg_parser.parse_args()
    _validate(args)
    _post_processing(args)

    return args


def main():
    args = _parse_args()
    _execute(args)

if __name__ == '__main__':
    main()
