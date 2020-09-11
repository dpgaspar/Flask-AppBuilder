import re

from flask import request


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
        re_match = re.match(r"page_(.*)", arg)
        if re_match:
            try:
                page_num = int(request.args.get(arg))
                if page_num >= 0:
                    pages[re_match.group(1)] = page_num
            except ValueError:
                pass
    return pages


def get_page_size_args():
    """
        Get page size arguments, returns an int
        { <VIEW_NAME>: PAGE_NUMBER }

        Arguments are passed: psize_<VIEW_NAME>=<PAGE_SIZE>

    """
    page_sizes = {}
    for arg in request.args:
        re_match = re.match(r"psize_(.*)", arg)
        if re_match:
            try:
                page_size = int(request.args.get(arg))
                if page_size >= 1:
                    page_sizes[re_match.group(1)] = page_size
            except ValueError:
                pass
    return page_sizes


def get_order_args():
    """
        Get order arguments, return a dictionary
        { <VIEW_NAME>: (ORDER_COL, ORDER_DIRECTION) }

        Arguments are passed like: _oc_<VIEW_NAME>=<COL_NAME>&_od_<VIEW_NAME>='asc'|'desc'

    """
    orders = {}
    for arg in request.args:
        re_match = re.match(r"_oc_(.*)", arg)
        if re_match:
            order_direction = request.args.get("_od_" + re_match.group(1))
            if order_direction in ("asc", "desc"):
                orders[re_match.group(1)] = (request.args.get(arg), order_direction)
    return orders


def get_filter_args(filters):
    filters.clear_filters()
    for arg in request.args:
        re_match = re.match(r"_flt_(\d)_(.*)", arg)
        if re_match:
            filter_index = int(re_match.group(1))
            col_name = re_match.group(2)
            try:
                filters.add_filter_index(col_name, filter_index, request.args.get(arg))
            except (KeyError, IndexError):
                pass
