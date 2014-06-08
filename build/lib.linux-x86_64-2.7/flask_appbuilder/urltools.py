import re
from flask import url_for, request

def get_group_by_args():
    """
        Get page arguments for group by
    """
    group_by = request.args.get('group_by')
    if not group_by: group_by = ''
    return group_by

def get_page_args():
    """
        Get page arguments, returns a dictionary
        { <VIEW_NAME>: PAGE_NUMBER }
    
        Arguments are passed: page_<VIEW_NAME>=<PAGE_NUMBER>
    
    """
    pages = {}
    for arg in request.args:
        re_match = re.findall('page_(.*)', arg)
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
        re_match = re.findall('psize_(.*)', arg)
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
        re_match = re.findall('_oc_(.*)', arg)
        if re_match:
            orders[re_match[0]] = (request.args.get(arg),request.args.get('_od_' + re_match[0]))
    return orders

def get_filter_args(filters):
    filters.clear_filters()
    for arg in request.args:
        re_match = re.findall('_flt_(\d)_(.*)', arg)
        if re_match:
            filters.add_filter_index(re_match[0][1], int(re_match[0][0]), request.args.get(arg))
