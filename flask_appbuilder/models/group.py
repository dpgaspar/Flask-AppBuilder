from __future__ import unicode_literals
import calendar
import logging
from itertools import groupby

log = logging.getLogger(__name__)


def aggregate_count(items, col):
    return len(list(items))


def aggregate_sum(items, col):
    value = 0
    for item in items:
        value = value + getattr(item, col)
    return value


def aggregate_avg(items, col):
    return aggregate_sum(items, col) / aggregate_count(items, col)


class BaseGroupBy(object):
    column_name = ''
    name = ''
    aggregate_func = None
    aggregate_col = ''

    def __init__(self, column_name, name, aggregate_func=aggregate_count, aggregate_col=''):
        """
            Constructor.

            :param column_name:
                Model field name
            :param name:
                The group by name

        """
        self.column_name = column_name
        self.name = name
        self.aggregate_func = aggregate_func
        self.aggregate_col = aggregate_col

    def apply(self, data):
        """
            Override this to implement you own new filters
        """
        pass

    def get_group_col(self, item):
        return getattr(item, self.column_name)

    def get_format_group_col(self, item):
        return (item)

    def get_aggregate_col_name(self):
        if self.aggregate_col:
            return self.aggregate_func.__name__ + '_' + self.aggregate_col
        else:
            return self.aggregate_func.__name__

    def __repr__(self):
        return self.name


class GroupByCol(BaseGroupBy):

    def _apply(self, data):
        data = sorted(data, key=self.get_group_col)
        json_data = dict()
        json_data['cols'] = [{'id': self.column_name,
                             'label': self.column_name,
                              'type': 'string'},
                             {'id': self.aggregate_func.__name__ + '_' + self.column_name,
                              'label': self.aggregate_func.__name__ + '_' + self.column_name,
                              'type': 'number'}]
        json_data['rows'] = []
        for (grouped, items) in groupby(data, self.get_group_col):
            aggregate_value = self.aggregate_func(items, self.aggregate_col)
            json_data['rows'].append(
                {"c": [{"v": self.get_format_group_col(grouped)}, {"v": aggregate_value}]})
        return json_data


    def apply(self, data):
        data = sorted(data, key=self.get_group_col)
        return [
            [self.get_format_group_col(grouped), self.aggregate_func(items, self.aggregate_col)]
            for (grouped, items) in groupby(data, self.get_group_col)
        ]


class GroupByDateYear(BaseGroupBy):
    def apply(self, data):
        data = sorted(data, key=self.get_group_col)
        return [
            [self.get_format_group_col(grouped), self.aggregate_func(items, self.aggregate_col)]
            for (grouped, items) in groupby(data, self.get_group_col)
        ]

    def get_group_col(self, item):
        value = getattr(item, self.column_name)
        if value:
            return value.year


class GroupByDateMonth(BaseGroupBy):
    def apply(self, data):
        data = sorted(data, key=self.get_group_col)
        return [
            [self.get_format_group_col(grouped), self.aggregate_func(items, self.aggregate_col)]
            for (grouped, items) in groupby(data, self.get_group_col)
            if grouped
        ]

    def get_group_col(self, item):
        value = getattr(item, self.column_name)
        if value:
            return value.year, value.month 

    def get_format_group_col(self, item):
        return calendar.month_name[item[1]] + ' ' + str(item[0])


class GroupBys(object):
    group_bys = None
    """
        [['COLNAME',GROUP_CLASS, AGR_FUNC,'AGR_COLNAME'],]
    """

    def __init__(self, group_bys):
        self.group_bys = group_bys

