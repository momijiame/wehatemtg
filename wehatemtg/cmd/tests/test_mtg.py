# -*- coding: utf-8 -*-

import sys

import nose
from nose.tools.trivial import eq_

from wehatemtg.cmd.mtg import (
    _parse_args,
    costs_integrator,
    DEFAULT_HOURS_WORKED_PER_DAY,
    DEFAULT_DAYS_WORKED_PER_MONTH,
    separate_comma_per_3digits
)


class Test_separate_comma_per_3digits(object):

    def test(self):
        eq_('100', separate_comma_per_3digits('100'))
        eq_('1,000', separate_comma_per_3digits('1000'))
        eq_('10,000', separate_comma_per_3digits('10000'))
        eq_('100,000', separate_comma_per_3digits('100000'))
        eq_('1,000,000', separate_comma_per_3digits('1000000'))
        eq_('10,000,000', separate_comma_per_3digits('10000000'))


class Test_costs_integrator(object):

    def test(self):
        hours_per_day = DEFAULT_HOURS_WORKED_PER_DAY
        days_per_month = DEFAULT_DAYS_WORKED_PER_MONTH
        hours_per_month = hours_per_day * days_per_month
        secs_per_year = hours_per_month * 12 * 3600
        # 年収を一年間の秒数と同じにして 1sec で 1JPY 稼ぐようにする
        params = {
            'annual_salary': secs_per_year,
            'hours_worked_per_day': None,
            'days_worked_per_month': None,
            'number_of_participants': None,
        }

        # カウンタと得られる値が一致すれば正常に動作している
        gen = costs_integrator(params)
        for i in range(1, 10):
            eq_(next(gen), i)

    def test_decimal_point(self):
        hours_per_day = DEFAULT_HOURS_WORKED_PER_DAY
        days_per_month = DEFAULT_DAYS_WORKED_PER_MONTH
        hours_per_month = hours_per_day * days_per_month
        secs_per_year = hours_per_month * 12 * 3600
        # 1sec で 0.1JPY 稼ぐようにする
        params = {
            'annual_salary': secs_per_year / 10,
        }

        # 10 カウント後に 1 が得られれば正常に動作している
        gen = costs_integrator(params)
        for _ in range(1, 10):
            eq_(next(gen), 0)
        eq_(next(gen), 1)


class Test_parse_args(object):

    def test_default(self):
        sys.argv = [
            'mtg',
        ]
        args = _parse_args()
        eq_(args.annual_salary, None)
        eq_(args.hours_worked_per_day, None)
        eq_(args.days_worked_per_month, None)
        eq_(args.number_of_participants, None)

if __name__ == "__main__":
    nose.main(argv=['nosetests', '-s', '-v'], defaultTest=__file__)
