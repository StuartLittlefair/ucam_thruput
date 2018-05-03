"""
Module for handling graph and component tables.

Largely copied and pasted from stsynphot (https://github.com/spacetelescope/stsynphot_refactor)
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import pkg_resources
import os

import numpy as np
from astropy import log
from astropy.table import Table


__all__ = ['GraphTable', 'CompTable']


class GraphTable(object):
    """Class to handle graph table.

    All string entries will be converted to lower case.
    Comment column is ignored.

    Parameters
    ----------
    graphfile : str
        Graph table name.

    Attributes
    ----------
    keywords : array of str
        Keyword names.

    compnames, thcompnames : array of str
        Components names (optical and thermal).

    innodes, outnodes : array of int
        Input and output nodes.
    """
    def __init__(self, graphfile):

        data = Table.read(graphfile)

        # Convert all strings to lowercase
        self.keywords = np.array([s.lower() for s in data['KEYWORD']])
        self.compnames = np.array([s.lower() for s in data['COMPNAME']])
        self.thcompnames = np.array([s.lower() for s in data['THCOMPNAME']])

        # Already int
        self.innodes = data['INNODE']
        self.outnodes = data['OUTNODE']

    def get_next_node(self, modes, innode):
        """Return the output node that matches an element from
        given list of modes, starting at the given input node.
        If no match found for the given modes, output node
        corresponding to default mode is used.
        If multiple matches are found, only the result for the
        latest matched mode is stored.
        .. note::
            This is only used for debugging.
        Parameters
        ----------
        modes : list of str
            List of modes.
        innode : int
            Starting input node.
        Returns
        -------
        outnode : int
            Matching output node, or -1 if given input node not found.
        """
        nodes = np.where(self.innodes == innode)[0]

        # No match
        if len(nodes) == 0:
            return -1

        # Output node for default mode
        defaultindex = np.where(self.keywords[nodes] == 'default')[0]

        if len(defaultindex) != 0:
            outnode = self.outnodes[nodes[defaultindex]]

        for mode in modes:
            index = np.where(self.keywords[nodes] == mode)[0]
            if len(index) > 0:
                outnode = self.outnodes[nodes[index]]

        return outnode[0]

    def get_comp_from_gt(self, modes, innode):
        """Return component names for the given modes by traversing
        the graph table, starting at the given input node.

        .. note::
            Extra debug messages available by setting logger to
            debug mode.

        Parameters
        ----------
        modes : list of str
            List of modes.
        innode : int
            Starting input node.

        Returns
        -------
        components, thcomponents : list of str
            Optical and thermal components.

        Raises
        ------
        ValueError
        """
        components = []
        thcomponents = []
        outnode = 0
        inmodes = set(modes)
        used_modes = set()
        count = 0

        while outnode >= 0:
            if outnode < 0:  # pragma: no cover
                log.debug('outnode={0} (stop condition).'.format(outnode))

            previous_outnode = outnode
            nodes = np.where(self.innodes == innode)

            # If there are no entries with this innode, we're done
            if len(nodes[0]) == 0:
                log.debug(
                    'innode={0} not found (stop condition).'.format(innode))
                break

            # Find the entry corresponding to the component named
            # 'default', because thats the one we'll use if we don't
            # match anything in the modes list
            if 'default' in self.keywords[nodes]:
                dfi = np.where(self.keywords[nodes] == 'default')[0][0]
                outnode = self.outnodes[nodes[0][dfi]]
                component = self.compnames[nodes[0][dfi]]
                thcomponent = self.thcompnames[nodes[0][dfi]]
                used_default = True
            else:
                # There's no default, so fail if nothing found in the
                # keyword matching step.
                outnode = -2
                component = thcomponent = None

            # Match something from the modes list
            for mode in modes:
                if mode in self.keywords[nodes]:
                    used_modes.add(mode)
                    index = np.where(self.keywords[nodes] == mode)
                    n_match = len(index[0])
                    if n_match > 1:
                        raise ValueError(
                            'ambiguous ObsMode {0} matches found for {1}'.format(n_match, mode))
                    idx = index[0][0]
                    component = self.compnames[nodes[0][idx]]
                    thcomponent = self.thcompnames[nodes[0][idx]]
                    outnode = self.outnodes[nodes[0][idx]]
                    used_default = False

            log.debug('innode={0} outnode={1} compname={2}'.format(
                innode, outnode, component))
            components.append(component)
            thcomponents.append(thcomponent)
            innode = outnode

            if outnode == previous_outnode:
                log.debug('innode={0} outnode={1} used_default={2}'.format(
                    innode, outnode, used_default))
                count += 1
                if count > 3:
                    log.debug('Same outnode={0} over 3 times (stop '
                              'condition)'.format(outnode))
                    break

        if outnode < 0:
            log.debug('outnode={0} (stop condition)'.format(outnode))
            raise ValueError(
                'incomplete ObsMode {0}, choose from {1}'.format(modes, self.keywords[nodes]))

        if inmodes != used_modes:
            raise ValueError(
                'unused keyword {0}'.format(str(inmodes.difference(used_modes))))

        return components, thcomponents


class CompTable(object):
    """Class to handle component table.

    Only component names and filenames are kept.

    Parameters
    ----------
    compfile : str
        Component table filename.

    Attributes
    ----------
    name : str
        Component table filename.

    compnames, filenames : array of str
        Component names and corresponding filenames.
    """
    def __init__(self, compfile):
        data = Table.read(compfile)
        self.name = compfile
        self.compnames = np.array([s.lower() for s in data['COMPNAME']])
        resource_dir = pkg_resources.resource_filename('ucam_thruput', 'data')
        self.filenames = np.array([
            os.path.join(resource_dir, fn) for fn in data['FILENAME']
        ])

    def get_filenames(self, compnames):
        """Get filenames of given component names.

        For multiple matches, only the first match is kept.

        Parameters
        ----------
        compnames : list of str
            List of component names to search. Case-sensitive.

        Returns
        -------
        files : list of str
            List of matched filenames.

        Raises
        ------
        ValueError
            Unmatched component name.
        """
        files = []
        for compname in compnames:
            if compname not in (None, '',  'clear'):
                index = np.where(self.compnames == compname)[0]
                if len(index) < 1:
                    raise ValueError(
                        'unmatched component: Cannot find {0} in {1}.'.format(compname, self.name))
                files.append(self.filenames[index[0]].lstrip())
            else:
                files.append('clear')

        return files
