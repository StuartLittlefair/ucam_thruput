from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from collections import namedtuple


BaseEdge = namedtuple("BaseEdge", ['innode', 'outnode', 'keywords', 'thruput_reference'])
Filter = namedtuple("Filter", ['name', 'thruput_reference'])


class Edge(BaseEdge):
    def __new__(cls, innode, outnode, thruput_reference, keywords=None):
        if keywords is None:
            keywords = ['default']
        else:
            keywords = keywords.split(',')
        self = super(Edge, cls).__new__(cls, innode, outnode, keywords, thruput_reference)
        return self

    def to_table_rows(self):
        return ((self.thruput_reference, kw, self.innode, self.outnode, 'clear', '') for kw in self.keywords)
