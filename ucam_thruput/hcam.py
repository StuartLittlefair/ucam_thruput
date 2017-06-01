from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import copy
from itertools import chain

from .structures import Edge, Filter


class Hcam:
    _filter_groupings = dict(
        u=[
            Filter('u', 'hcam_u'),
            Filter('u_s', 'hcam_u_s')
        ],
        g=[
            Filter('g', 'hcam_g'),
            Filter('g_s', 'hcam_g_s')
        ],
        r=[
            Filter('r', 'hcam_r'),
            Filter('r_s', 'hcam_r_s')
        ],
        i=[
            Filter('i', 'hcam_i'),
            Filter('i_s', 'hcam_i_s')
        ],
        z=[
            Filter('z', 'hcam_z'),
            Filter('z_s', 'hcam_z_s'),
            Filter('Y', 'hcam_y')
        ]
    )

    _edge_list = [
        Edge(12, 1201, 'clear', 'gtc'),
        Edge(12, 1202, 'clear', 'wht'),
        Edge(1201, 1203, 'hcam_coll_gtc'),
        Edge(1202, 1203, 'hcam_coll_wht'),
        Edge(1203, 1204, 'hcam_dich3_trans'),
        Edge(1204, 1207, 'hcam_dich4_trans'),
        Edge(1205, 1207, 'hcam_dich2_trans'),
        Edge(1206, 1207, 'hcam_dich1_trans'),
        Edge(1209, 1214, 'clear'),
        Edge(1210, 1215, 'clear'),
        Edge(1211, 1215, 'clear'),
        Edge(1212, 1216, 'clear'),
        Edge(1213, 1216, 'clear'),
        Edge(1214, 1217, 'hcam_win_blu'),
        Edge(1215, 1218, 'hcam_win_grn'),
        Edge(1216, 1219, 'hcam_win_red'),
        Edge(1217, 999, 'hcam_ccd_blu'),
        Edge(1218, 999, 'hcam_ccd_grn'),
        Edge(1219, 999, 'hcam_ccd_red')
    ]

    _formattable_edges = {
        'u': [(1203, 1205, 'hcam_dich3_reflec'), (1205, 1206, 'hcam_dich2_reflec'),
              (1206, 1207, 'hcam_dich1_reflec'), (1208, 1209, 'hcam_cam_u')],
        'g': [(1203, 1205, 'hcam_dich3_reflec'), (1205, 1206, 'hcam_dich2_reflec'), (1208, 1210, 'hcam_cam_g')],
        'r': [(1203, 1205, 'hcam_dich3_reflec'), (1208, 1211, 'hcam_cam_r')],
        'i': [(1204, 1207, 'hcam_dich4_reflec'), (1208, 1212, 'hcam_cam_i')],
        'z': [(1208, 1213, 'hcam_cam_z')]
    }

    _node_list = [
        ((12, 999), 'main'),
        ((1201, 1202), 'collimator'),
        ((1203,), 'dichroic #3'),
        ((1204,), 'dichroic #4'),
        ((1205,), 'dichroic #2'),
        ((1206,), 'dichroic #1'),
        ((1207,), 'filters'),
        ((1208, 1209, 1210, 1211, 1212, 1213), 'cameras'),
        ((1214, 1215, 1216), 'CCD windows'),
        ((1217, 1218, 1219), 'CCDs')
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
            retlist.append(Edge(1207, 1208, 'filter'))
        # add edges by colour groups for dichroics
        for group in self._filter_groupings:
            edgespec_list = self._formattable_edges[group]
            for edgespec in edgespec_list:
                innode, outnode, component = edgespec
                edge = Edge(innode, outnode, component, group)
                retlist.append(edge)

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
            edge = Edge(1207, 1208, filt.thruput_reference, filt.name)
            yield from edge.to_table_rows()

        # now add appropriate edges for dichroics and cams
        # grouping filters together

        for group in self._filter_groupings:
            edgespec_list = self._formattable_edges[group]
            for edgespec in edgespec_list:
                innode, outnode, component = edgespec
                for filt in self._filter_groupings[group]:
                    edge = Edge(innode, outnode, component, filt.name)
                    yield from edge.to_table_rows()

    @property
    def complete_edgelist(self):
        """
        All edges for full, non-simplyfied, graph
        """
        yield from self._edge_list
        for filt in chain(*self._filter_groupings.values()):
            edge = Edge(1207, 1208, filt.thruput_reference, filt.name)
            yield edge

        # now add appropriate edges for dichroics and cams
        # grouping filters together
        for group in self._filter_groupings:
            edgespec_list = self._formattable_edges[group]
            for edgespec in edgespec_list:
                innode, outnode, component = edgespec
                for filt in self._filter_groupings[group]:
                    edge = Edge(innode, outnode, component, filt.name)
                    yield edge
