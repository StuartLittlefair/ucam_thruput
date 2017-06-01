"""
Encoding of light path for ultraspec.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import copy

from .structures import Edge, Filter


class Uspec:
    _filter_list = [
        Filter('u', 'uspec_u'),
        Filter('g', 'uspec_g'),
        Filter('r', 'uspec_r'),
        Filter('i', 'uspec_i'),
        Filter('z', 'uspec_z'),
        Filter('kg5', 'uspec_kg5'),
        Filter('bowen', 'uspec_bowen'),
        Filter('n86', 'uspec_n86'),
        Filter('rcont', 'uspec_rcont'),
        Filter('ha_broad', 'uspec_ha_broad'),
        Filter('bcont', 'uspec_bcont'),
        Filter('ha_narrow', 'uspec_ha_narrow'),
        Filter('iz', 'uspec_iz'),
        Filter('NaI', 'uspec_nai'),
        Filter('clear', 'uspec_clear')
    ]

    _edge_list = [
        Edge(13, 131, 'clear'),
        Edge(131, 132, 'uspec_barrel3'),
        Edge(133, 134, 'uspec_barrel2'),
        Edge(134, 135, 'uspec_barrel1'),
        Edge(135, 136, 'uspec_window'),
        Edge(136, 999, 'uspec_ccd')
    ]

    _node_list = [
        ((13, 999), 'main'),
        ((131,), 'barrel3'),
        ((132,), 'filters'),
        ((133,), 'barrel2'),
        ((134,), 'barrel1'),
        ((135,), 'window'),
        ((136,), 'CCD')
    ]

    @property
    def nodelist(self):
        return self._node_list

    @property
    def edgelist(self):
        """
        Schematic list of edges for plotting graph
        """
        retlist = copy.copy(self._edge_list)
        # illustrative edges for filters
        for i in range(10):
            retlist.append(Edge(132, 133, 'filter'))
        return retlist

    @property
    def instrument_table_rows(self):
        """
        A generator function to iterate over table rows
        """
        for edge in self._edge_list:
            yield from edge.to_table_rows()
        for filt in self._filter_list:
            edge = Edge(132, 133, filt.thruput_reference, filt.name)
            yield from edge.to_table_rows()

    @property
    def complete_edgelist(self):
        """
        All edges for full, non-simplyfied, graph
        """
        yield from self._edge_list
        for filt in self._filter_list:
            edge = Edge(132, 133, filt.thruput_reference, filt.name)
            yield edge
