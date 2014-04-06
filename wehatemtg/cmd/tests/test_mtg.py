# -*- coding: utf-8 -*-

import sys

import nose
from nose.tools.trivial import eq_
from nose.tools.nontrivial import raises

from wehatemtg.cmd.mtg import (
    _parse_args,
    separate_comma_per_3digits,
    CostIntegrator,
    floor_decimal,
    DEFAULT_CURRENCY,
    DEFAULT_HOURS_WORKED_PER_DAY,
    DEFAULT_DAYS_WORKED_PER_MONTH,
    DEFAULT_NUMBER_OF_PARTICIPANTS,
    Currencies
)


class Test_separate_comma_per_3digits(object):

    def test(self):
        eq_('100', separate_comma_per_3digits('100'))
        eq_('1,000', separate_comma_per_3digits('1000'))
        eq_('10,000', separate_comma_per_3digits('10000'))
        eq_('100,000', separate_comma_per_3digits('100000'))
        eq_('1,000,000', separate_comma_per_3digits('1000000'))
        eq_('10,000,000', separate_comma_per_3digits('10000000'))

    def test_point(self):
        eq_('100.00', separate_comma_per_3digits('100.00'))
        eq_('1,000.00', separate_comma_per_3digits('1000.00'))
        eq_('10,000.00', separate_comma_per_3digits('10000.00'))
        eq_('100,000.00', separate_comma_per_3digits('100000.00'))
        eq_('1,000,000.00', separate_comma_per_3digits('1000000.00'))
        eq_('10,000,000.00', separate_comma_per_3digits('10000000.00'))


class Test_costs_integrator(object):

    def test(self):
        hours_per_day = DEFAULT_HOURS_WORKED_PER_DAY
        days_per_month = DEFAULT_DAYS_WORKED_PER_MONTH
        hours_per_month = hours_per_day * days_per_month
        secs_per_year = hours_per_month * 12 * 3600
        jpy = 10000
        # 年収を一年間の秒数と同じにして 1sec で 1JPY 稼ぐようにする
        params = {
            'annual_salary': float(secs_per_year) / jpy,
            'currency': DEFAULT_CURRENCY,
            'hours_worked_per_day': DEFAULT_HOURS_WORKED_PER_DAY,
            'days_worked_per_month': DEFAULT_DAYS_WORKED_PER_MONTH,
            'number_of_participants': DEFAULT_NUMBER_OF_PARTICIPANTS,
        }

        # カウンタと得られる値が一致すれば正常に動作している
        ite = CostIntegrator(params)
        for i in range(1, 10):
            eq_(floor_decimal(next(ite)), i)

    def test_decimal_point(self):
        hours_per_day = DEFAULT_HOURS_WORKED_PER_DAY
        days_per_month = DEFAULT_DAYS_WORKED_PER_MONTH
        hours_per_month = hours_per_day * days_per_month
        secs_per_year = hours_per_month * 12 * 3600
        jpy = 10000
        # 1sec で 0.1JPY 稼ぐようにする
        params = {
            'annual_salary': float(secs_per_year) / jpy / 10,
            'currency': DEFAULT_CURRENCY,
            'hours_worked_per_day': DEFAULT_HOURS_WORKED_PER_DAY,
            'days_worked_per_month': DEFAULT_DAYS_WORKED_PER_MONTH,
            'number_of_participants': DEFAULT_NUMBER_OF_PARTICIPANTS,
        }

        # 10 カウント後に 1 が得られれば正常に動作している
        ite = CostIntegrator(params)
        for _ in range(1, 10):
            eq_(floor_decimal(next(ite)), 0)
        eq_(floor_decimal(next(ite)), 1)


class Test_parse_args(object):

    def test_default(self):
        sys.argv = [
            'mtg',
        ]
        args = _parse_args()
        eq_(args.annual_salary, Currencies.salary(DEFAULT_CURRENCY))
        eq_(args.currency, DEFAULT_CURRENCY)
        eq_(args.hours_worked_per_day, DEFAULT_HOURS_WORKED_PER_DAY)
        eq_(args.days_worked_per_month, DEFAULT_DAYS_WORKED_PER_MONTH)
        eq_(args.number_of_participants, DEFAULT_NUMBER_OF_PARTICIPANTS)

    def test_ok_currency_usd(self):
        sys.argv = [
            'mtg',
            '-c',
            'USD',
        ]
        args = _parse_args()
        eq_(args.currency, 'USD')
        eq_(args.annual_salary, Currencies.salary('USD'))

    @raises(ValueError)
    def test_ng_currency(self):
        sys.argv = [
            'mtg',
            '-c',
            'XXX',
        ]
        _parse_args()


if __name__ == "__main__":
    nose.main(argv=['nosetests', '-s', '-v'], defaultTest=__file__)
