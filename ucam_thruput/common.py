"""
Encoding of light path which is common to all instruments.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


from .structures import Edge


class Common:
    def __init__(self):
        self.edgelist = [
            Edge(1, 2, 'atmos'),
            Edge(1, 2, 'clear', 'noatmos'),
            Edge(2, 3, 'alum'),
            Edge(3, 4, 'alum'),
            Edge(3, 6, 'alum', 'wht'),
            Edge(4, 5, 'alum', 'tnt,cube'),
            Edge(4, 6, 'alum'),
            Edge(5, 6, 'alum'),
            Edge(6, 7, 'clear', 'hcam'),
            Edge(6, 10, 'clear'),
            Edge(7, 10, 'scint_corr', 'scint_corr'),
            Edge(7, 10, 'clear'),
            Edge(10, 11, 'clear', 'ucam'),
            Edge(10, 12, 'clear', 'hcam'),
            Edge(10, 13, 'clear', 'uspec')
        ]

        self.nodelist = [
            ((1,), 'atmosphere'),
            ((2,), '1ry'),
            ((3,), '2ry'),
            ((4,), '3ry'),
            ((5,), '4ry'),
            ((6, 7), 'scintillation'),
            ((10, 11, 12, 13), 'main')
        ]

    @property
    def instrument_table_rows(self):
        """
        A generator function to iterate over table rows
        """
        for edge in self.edgelist:
            yield from edge.to_table_rows()

    @property
    def complete_edgelist(self):
        yield from self.edgelist
