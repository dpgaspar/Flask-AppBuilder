from __future__ import unicode_literals


def dict_to_json(xcol, ycols, labels, value_columns):
    """
        Converts a list of dicts from datamodel query results
        to google chart json data.

        :param xcol:
            The name of a string column to be used has X axis on chart
        :param ycols:
            A list with the names of series cols, that can be used as numeric
        :param labels:
            A dict with the columns labels.
        :param value_columns:
            A list of dicts with the values to convert
    """
    json_data = dict()
    json_data['cols'] = [{'id': xcol,
                          'label': unicode(labels[xcol]),
                          'type': 'string'}]
    for ycol in ycols:
        json_data['cols'].append({'id': ycol,
                                  'label': unicode(labels[ycol]),
                                  'type': 'number'})
    json_data['rows'] = []
    for value in value_columns:
        row = {'c': []}
        for ycol in ycols:
            row['c'].append({'v': (value[xcol])})
            if value[ycol]:
                row['c'].append({'v': int(value[ycol])})
            else:
                row['c'].append({'v': 0})
        json_data['rows'].append(row)
    return json_data
