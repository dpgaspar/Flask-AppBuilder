import logging
import re

from flask import request

log = logging.getLogger(__name__)


class Stack(object):
    """
        Stack data structure will not insert
        equal sequential data
    """

    def __init__(self, list=None, size=5):
        self.size = size
        self.data = list or []

    def push(self, item):
        if self.data:
            if item != self.data[len(self.data) - 1]:
                self.data.append(item)
        else:
            self.data.append(item)
        if len(self.data) > self.size:
            self.data.pop(0)

    def pop(self):
        if len(self.data) == 0:
            return None
        return self.data.pop(len(self.data) - 1)

    def to_json(self):
        return self.data


def get_group_by_args():
    """
        Get page arguments for group by
    """
    group_by = request.args.get("group_by")
    if not group_by:
        group_by = ""
    return group_by


def get_page_args():
    """
        Get page arguments, returns a dictionary
        { <VIEW_NAME>: PAGE_NUMBER }

        Arguments are passed: page_<VIEW_NAME>=<PAGE_NUMBER>

    """
    pages = {}
    for arg in request.args:
        re_match = re.findall("page_(.*)", arg)
        if re_match:
            pages[re_match[0]] = int(request.args.get(arg))
    return pages


def get_page_size_args():
    """
        Get page size arguments, returns an int
        { <VIEW_NAME>: PAGE_NUMBER }

        Arguments are passed: psize_<VIEW_NAME>=<PAGE_SIZE>

    """
    page_sizes = {}
    for arg in request.args:
        re_match = re.findall("psize_(.*)", arg)
        if re_match:
            page_sizes[re_match[0]] = int(request.args.get(arg))
    return page_sizes


def get_order_args():
    """
        Get order arguments, return a dictionary
        { <VIEW_NAME>: (ORDER_COL, ORDER_DIRECTION) }

        Arguments are passed like: _oc_<VIEW_NAME>=<COL_NAME>&_od_<VIEW_NAME>='asc'|'desc'

    """
    orders = {}
    for arg in request.args:
        re_match = re.findall("_oc_(.*)", arg)
        if re_match:
            order_direction = request.args.get("_od_" + re_match[0])
            if order_direction in ("asc", "desc"):
                orders[re_match[0]] = (request.args.get(arg), order_direction)
    return orders


def get_filter_args(filters, disallow_if_not_in_search=True):
    """
    Sets filters with the given current request args

    Request arg filters are of the form "_flt_<DECIMAL>_<VIEW_NAME>_<COL_NAME>"

    :param filters: Filter instance to apply the request filters on
    :param disallow_if_not_in_search: If True, disallow filters that are not in the search
    :return:
    """
    filters.clear_filters()
    request_args = set(request.args)
    for arg in request_args:
        re_match = re.findall(r"_flt_(\d)_(.*)", arg)
        if not re_match:
            continue
        filter_index = int(re_match[0][0])
        filter_column = re_match[0][1]
        if (
            filter_column not in filters.get_search_filters().keys()
            and disallow_if_not_in_search
        ):
            log.warning("Filter column not allowed")
            continue
        filters.add_filter_index(filter_column, filter_index, request.args.getlist(arg))
