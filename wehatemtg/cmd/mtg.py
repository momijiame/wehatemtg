#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import curses
import time
from decimal import Decimal, ROUND_DOWN
from abc import ABCMeta, abstractmethod
import signal

from pyfiglet import Figlet

DEFAULT_ANNUAL_SALARY = 4080000
DEFAULT_HOURS_WORKED_PER_DAY = 8
DEFAULT_DAYS_WORKED_PER_MONTH = 20
DEFAULT_NUMBER_OF_PARTICIPANTS = 1


def costs_integrator(salary_params=None):
    salary_params = salary_params or {}

    annual_salary = salary_params.get(
        'annual_salary',
        DEFAULT_ANNUAL_SALARY
    ) or DEFAULT_ANNUAL_SALARY
    hours_worked_per_day = salary_params.get(
        'hours_worked_per_day',
        DEFAULT_HOURS_WORKED_PER_DAY
    ) or DEFAULT_HOURS_WORKED_PER_DAY
    days_worked_per_month = salary_params.get(
        'days_worked_per_month',
        DEFAULT_DAYS_WORKED_PER_MONTH
    ) or DEFAULT_DAYS_WORKED_PER_MONTH
    number_of_participants = salary_params.get(
        'number_of_participants',
        DEFAULT_NUMBER_OF_PARTICIPANTS
    ) or DEFAULT_NUMBER_OF_PARTICIPANTS

    hours_worked_per_month = hours_worked_per_day * days_worked_per_month
    seconds_worked_per_year = 12 * hours_worked_per_month * 3600
    salary_per_second = Decimal(annual_salary) / seconds_worked_per_year

    total = 0
    while True:
        total += salary_per_second * number_of_participants
        # 小数点は切り捨てる
        yield total.quantize(Decimal('1.'), rounding=ROUND_DOWN)


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
    separate_positions = range(len(str_n), 0, -3) + [0]
    separate_tuple_positions = [
        (separate_positions[i], separate_positions[i + 1])
        for i in range(len(separate_positions) - 1)
    ]
    str_n_pieces = [
        str_n[start:end]
        for end, start in separate_tuple_positions
    ]
    str_n_pieces.reverse()
    return ','.join(str_n_pieces)


class CostsScreen(PeriodicScreen):

    def __init__(self, integrator):
        super(CostsScreen, self).__init__()
        self.integrator = integrator

    def show(self):
        costs = next(self.integrator)
        separated_costs = separate_comma_per_3digits(costs)
        return '{0} JPY'.format(separated_costs)


class DecoratedCostsScreen(CostsScreen):

    def __init__(self, integrator, font='big'):
        super(CostsScreen, self).__init__()
        self.integrator = integrator
        self.fighler = Figlet(font=font)

    def show(self):
        data = super(DecoratedCostsScreen, self).show()
        return self.fighler.renderText(data)


def execute(args):
    salary_params = {
        'annual_salary': args.annual_salary,
        'hours_worked_per_day': args.hours_worked_per_day,
        'days_worked_per_month': args.days_worked_per_month,
        'number_of_participants': args.number_of_participants,
    }
    integrator = costs_integrator(salary_params)
    screen = DecoratedCostsScreen(integrator)
    screen.start()


def _parse_args():
    description = 'We hate meeting'
    arg_parser = argparse.ArgumentParser(description=description)

    option_s_help = 'Member\'s average annual salary'
    arg_parser.add_argument(
        '-s', '--annual-salary',
        type=int,
        required=False, default=None,
        help=option_s_help,
    )

    option_t_help = 'Member\'s average hours worked per day'
    arg_parser.add_argument(
        '-t', '--hours-worked-per-day',
        type=int,
        required=False, default=None,
        help=option_t_help,
    )

    option_d_help = 'Member\'s average days worked per month'
    arg_parser.add_argument(
        '-d', '--days-worked-per-month',
        type=int,
        required=False, default=None,
        help=option_d_help,
    )

    option_d_help = 'The number of participants of the meeting'
    arg_parser.add_argument(
        '-n', '--number-of-participants',
        type=int,
        required=False, default=None,
        help=option_d_help,
    )

    args = arg_parser.parse_args()
    return args


def main():
    args = _parse_args()
    execute(args)

if __name__ == '__main__':
    main()
