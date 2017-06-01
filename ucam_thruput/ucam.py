from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import copy
from itertools import chain

from .structures import Edge, Filter


class Ucam:
    _filter_groupings = dict(
        u=[
            Filter('u', 'ucam_u'),
            Filter('3500_nb', 'ucam_3500_nb'),
            Filter('u_s', 'ucam_u_s')
        ],
        g=[
            Filter('g', 'ucam_g'),
            Filter('g_s', 'ucam_g_s'),
            Filter('4170_nb', 'ucam_4170_nb'),
            Filter('bowen', 'ucam_bowen'),
            Filter('bcont', 'ucam_bcont')
        ],
        riz=[
            Filter('r', 'ucam_r'),
            Filter('i', 'ucam_i'),
            Filter('z', 'ucam_z'),
            Filter('r_s', 'ucam_r_s'),
            Filter('i_s', 'ucam_i_s'),
            Filter('z_s', 'ucam_z_s'),
            Filter('clear', 'ucam_clear'),
            Filter('rcont', 'ucam_rcont'),
            Filter('NaI', 'ucam_nai'),
            Filter('ha_broad', 'ucam_ha_broad'),
            Filter('ha_narrow', 'ucam_ha_narrow'),
            Filter('iz', 'ucam_iz')
        ]
    )

    _edge_list = [
        Edge(11, 111, 'clear', 'vlt'),
        Edge(11, 112, 'clear', 'wht'),
        Edge(11, 113, 'clear', 'ntt'),
        Edge(111, 114, 'ucam_coll_vlt'),
        Edge(112, 114, 'ucam_coll_wht'),
        Edge(113, 114, 'ucam_coll_ntt'),
        Edge(113, 114, 'ucam_coll_ntt_old', 'old'),
        Edge(114, 115, 'ucam_dich1_trans'),
        Edge(115, 118, 'ucam_dich2_trans'),
        Edge(118, 119, 'ucam_cam_red'),
        Edge(117, 119, 'ucam_cam_grn'),
        Edge(116, 119, 'ucam_cam_bl'),
        Edge(120, 121, 'ucam_ccd_windows')
    ]

    _node_list = [
        ((11, 999), 'main'),
        ((111, 112, 113), 'collimator'),
        ((114,), 'dichroic #1'),
        ((115,), 'dichroic #2'),
        ((116, 117, 118), 'cameras'),
        ((119,), 'filters'),
        ((120,), 'CCD windows'),
        ((121,), 'CCDs')
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
            retlist.append(Edge(119, 120, 'filter'))
        # add edges by colour groups for dichroics
        retlist.append(Edge(114, 115, 'ucam_dich1_reflec', 'u'))
        retlist.append(Edge(115, 117, 'ucam_dich2_reflec', 'g'))
        retlist.append(Edge(121, 999, 'ucam_ccd_blu', 'u')),
        retlist.append(Edge(121, 999, 'ucam_ccd_grn', 'g')),
        retlist.append(Edge(121, 999, 'ucam_ccd_red'))
        return retlist

    @property
    def instrument_table_rows(self):
        """
        A generator function to iterate over table rows
        """
        for edge in self._edge_list:
            yield from edge.to_table_rows()
        # now add a filter row for every filter
        for filt in chain(*self._filter_groupings.values()):
            edge = Edge(119, 120, filt.thruput_reference, filt.name)
            yield from edge.to_table_rows()
        # now add appropriate edges for dichroics and cameras,
        # grouping filters together
        for filt in self._filter_groupings['u']:
            edge = Edge(114, 116, 'ucam_dich1_reflec', filt.name)
            yield from edge.to_table_rows()
            edge = Edge(121, 999, 'ucam_ccd_blu', filt.name)
            yield from edge.to_table_rows()
        for filt in self._filter_groupings['g']:
            edge = Edge(115, 117, 'ucam_dich2_reflec', filt.name)
            yield from edge.to_table_rows()
            edge = Edge(121, 999, 'ucam_ccd_grn', filt.name)
            yield from edge.to_table_rows()
        for filt in self._filter_groupings['riz']:
            edge = Edge(121, 999, 'ucam_ccd_red', filt.name)
            yield from edge.to_table_rows()

    @property
    def complete_edgelist(self):
        """
        All edges for full, non-simplyfied, graph
        """
        yield from self._edge_list
        for filt in chain(*self._filter_groupings.values()):
            edge = Edge(119, 120, filt.thruput_reference, filt.name)
            yield edge
        # now add appropriate edges for dichroics and cameras,
        # grouping filters together
        for filt in self._filter_groupings['u']:
            edge = Edge(114, 116, 'ucam_dich1_reflec', filt.name)
            yield edge
            edge = Edge(121, 999, 'ucam_ccd_blu', filt.name)
            yield edge
        for filt in self._filter_groupings['g']:
            edge = Edge(115, 117, 'ucam_dich2_reflec', filt.name)
            yield edge
            edge = Edge(121, 999, 'ucam_ccd_grn', filt.name)
            yield edge
        for filt in self._filter_groupings['riz']:
            edge = Edge(121, 999, 'ucam_ccd_red', filt.name)
            yield edge
