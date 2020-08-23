# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 
#
# MDAnalysis --- https://www.mdanalysis.org
# Copyright (c) 2006-2017 The MDAnalysis Development Team and contributors
# (see the file AUTHORS for the full list of names)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# R. J. Gowers, M. Linke, J. Barnoud, T. J. E. Reddy, M. N. Melo, S. L. Seyler,
# D. L. Dotson, J. Domanski, S. Buchoux, I. M. Kenney, and O. Beckstein.
# MDAnalysis: A Python package for the rapid analysis of molecular dynamics
# simulations. In S. Benthall and S. Rostrup editors, Proceedings of the 15th
# Python in Science Conference, pages 102-109, Austin, TX, 2016. SciPy.
# doi: 10.25080/majora-629e541a-00e
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#

import numpy as np

from .base import TopologyReaderBase
from ..core.topology import Topology
from ..core.topologyattrs import (
    Atomids,
    Atomnames,
    Bonds,
    ChainIDs,
    Elements,
    Masses,
    Resids,
    Resnums,
    Resnames,
    Segids,
)


class OpenMMTopologyParser(TopologyReaderBase):
    format = 'OPENMMTOPOLOGY'

    @staticmethod
    def _format_hint(thing):
        """Can this Parser read object *thing*?

        .. versionadded:: 1.0.0
        """
        try:
            from simtk.openmm import app
        except ImportError:  
            return False
        else:
            return isinstance(thing, app.Topology)


    def parse(self, **kwargs):
        omm_topology = self.filename

        top = _mda_topology_from_omm_topology(omm_topology)

        return top

class OpenMMSimulationParser(TopologyReaderBase):
    format = 'OPENMMSIMULATION'

    @staticmethod
    def _format_hint(thing):
        """Can this Parser read object *thing*?

        .. versionadded:: 1.0.0
        """
        try:
            from simtk.openmm import app
        except ImportError:  
            return False
        else:
            return isinstance(thing, app.Simulation)


    def parse(self, **kwargs):
        omm_topology = self.filename.topology

        top = _mda_topology_from_omm_topology(omm_topology)

        return top

class OpenMMPDBFileParser(TopologyReaderBase):
    format = 'OPENMMPDBFILE'

    @staticmethod
    def _format_hint(thing):
        """Can this Parser read object *thing*?

        .. versionadded:: 1.0.0
        """
        try:
            from simtk.openmm import app
        except ImportError:  
            return False
        else:
            return isinstance(thing, app.PDBFile)


    def parse(self, **kwargs):
        omm_pdbfile = self.filename

        top = _mda_topology_from_omm_topology(omm_pdbfile.topology)

        return top

class OpenMMModellerParser(TopologyReaderBase):
    format = 'OPENMMMODELLER'

    @staticmethod
    def _format_hint(thing):
        """Can this Parser read object *thing*?

        .. versionadded:: 1.0.0
        """
        try:
            from simtk.openmm import app
        except ImportError:  
            return False
        else:
            return isinstance(thing, app.Modeller)


    def parse(self, **kwargs):
        omm_modeller = self.filename

        top = _mda_topology_from_omm_topology(omm_modeller.topology)

        return top



def _mda_topology_from_omm_topology(omm_topology):
    """ Construct mda topology from omm topology 

    Can be used for any openmm object that contains a topology object"""
    atom_resindex = [a.residue.index for a in omm_topology.atoms()]
    residue_segindex = [r.chain.index for r in omm_topology.residues()]
    atomids = [a.id for a in omm_topology.atoms()]
    atomnames = [a.name for a in omm_topology.atoms()]
    chainids = [a.residue.chain.id for a in omm_topology.atoms()]
    elements = [a.element.symbol for a in omm_topology.atoms()]
    masses = [a.element.mass._value for a in omm_topology.atoms()]
    resnames = [r.name for r in omm_topology.residues()]
    resids = [r.index for r in omm_topology.residues()]
    resnums = resids.copy()
    segids = [c.index for c in omm_topology.chains()]
    bonds = [(b.atom1.index, b.atom2.index) for b in omm_topology.bonds()]
    bond_orders =[b.order for b in omm_topology.bonds()]
    bond_types = [b.type for b in omm_topology.bonds()]
    
    n_atoms = len(atomids)
    n_residues = len(resids)
    n_segments = len(segids)
    
    attrs = [
        Atomids(np.array(atomids, dtype=np.int32)),
        Atomnames(np.array(atomnames, dtype=object)),
        Bonds(bonds, types=bond_types, order=bond_orders, guessed=False),
        ChainIDs(np.array(chainids, dtype=object)),
        Elements(np.array(elements, dtype=object)),
        Masses(np.array(masses, dtype=np.float32)),
        Resids(resids),
        Resnums(resnums),
        Resnames(resnames),
        Segids(segids)
    ]

    top = Topology(n_atoms, n_residues, n_segments, 
        attrs=attrs,
        atom_resindex=atom_resindex,
        residue_segindex=residue_segindex
    )

    return top


