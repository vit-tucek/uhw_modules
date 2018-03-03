# -*- coding: utf-8 -*-
r"""
uhw_modules

This module contains auxiliary classes and (monkey) patches for Sage classes which (hopefully) eventually will get merged into Sage.

AUTHORS:

- Vít Tuček: initial implementation
"""
from sage.categories.sets_cat import cartesian_product
from sage.combinat.posets.posets import Poset
from sage.combinat.root_system.weyl_group import WeylGroup
from sage.misc.cachefunc import cached_method
#from sage.all import cached_method
#from Cython.Utils import cached_method
from sage.geometry.fan import Fan
from sage.graphs.digraph import DiGraph
from sage.misc.latex import latex


class RootSystemFacets:
    """
    Class for facets of root systems. If two weights are in the same facets then the corresponding infinitesimal blocks of category O are equivalent.
    See chapter 7 of Humphreys: Representations of semisimple Lie algebras in the BGG category O
    """
    def __init__(self, cartan_type):
        self.cartan_type = cartan_type
        self.weyl_group = WeylGroup(self.cartan_type, prefix="s")
        self.ambient_space = self.weyl_group.domain()
        self.rho = self.ambient_space.rho()

    @cached_method
    def _get_fan(self):
        """
        Construct the fan of the root system so we have easy access to all facets.
        """
        rays = self.ambient_space.positive_roots()
        cones = [[g.action(v) for v in self.ambient_space.fundamental_weights()] for g in self.weyl_group]
        rays = list(set(v for cone in cones for v in cone))
        #print rays
        if self.ambient_space.dimension() == len(self.ambient_space.simple_roots()):
            cones = [[rays.index(x) for x in cone] for cone in cones]
            rays = map(lambda x: x.to_vector(), rays)
        else: # we need to raise the dimension of the cones and work in a quotient space / intersect with hyperplane
            cones = [[rays.index(x) for x in cone] + [len(rays)] for cone in cones]
            rays = map(lambda x: x.to_vector(), rays) + [(1,)*self.ambient_space.dimension()]
        return Fan(cones=cones, rays=rays)
    
    def facets(self, dim=None, codim=None): 
        """
        Iterate over cones of root system fan of dimension d and return them as polyhedron shifted to -rho. 
        """
        for cone in self._get_fan().cones(dim=dim, codim=codim):
            yield (cone.polyhedron() - self.rho).to_vector()
        

class RootWithScalarProduct:
    """
    Use this to relabel graphs of positive roots with scalar product with given weight v.
    """
    def __init__(self, r, v):
        self.root = r
        self.scalarproduct = v.dot_product(r.associated_coroot().to_vector())

    def _latex_(self):
        return "(%s, %s)" % (latex(self.scalarproduct), latex(self.root))

    def __str__(self):
        return str(self.scalarproduct)

    def __repr__(self):
        return repr(self.scalarproduct)


def _fix_basis_latex(string):
    """
    Basis of Ambient spaces are indexed by e_0, ..., e_{n-1} instead of conventional \epsilon_1, ..., \epsilon_n.
    This functions returns string with fixed LaTeX source. You can render its output in notebook by calling latex.eval(...)
    """
    import re
    def shift_number(matchobj):
        return "e_{%d}" % (int(matchobj.group(1)) + 1)

    index_re = re.compile("e_{(\d+)}")
    return index_re.sub(shift_number, string).replace("e_{", "\epsilon_{")

def fix_basis_latex(obj):
    return _fix_basis_latex(str(latex(obj))).replace("0000000000000", "")

def get_poset_latex(poset, orientation="up"):
    hd = poset.hasse_diagram()
    if orientation != "up":
        hd.set_latex_options(rankdir=orientation)

    return fix_basis_latex(latex(hd))

def poset_scalar_product(poset, v, only_nonnegative=True):
    """
    Returns LaTeX code of poset of roots whose nodes were labeled by inner product of those roots with give weight v.
    """
    p = poset.relabel(lambda r: RootWithScalarProduct(r, v))
    if only_nonnegative:
        p = p.subposet([x for x in p if not(x.scalarproduct < 0)])
    if p.is_empty():
        print("Poset of scalar products is empty.")
    return p

def WG_action(w, v):
    """
    Action of weyl group element w on vector v.
    Workaround for subgroups not containing elements of the supergroup.
    """
    AS = v.parent()
    return AS.from_vector(w.matrix()*v.to_vector())

def get_length_function(positive_roots):
    positive_roots = set(positive_roots)
    @cached_function
    def l(w):
        return len([a for a in positive_roots if WG_action(w.inverse(), -a) in positive_roots])
    return l

def generate_subgroup(generators):
    """
    Keep multiplying and taking inverses as long as new elements are constructed.
    Unfortunately, this routine takes too much time in practice.
    """
    new = set(a*b for (a,b) in cartesian_product([generators, generators])).union(set(g.inverse() for g in generators))
    if new == generators:
        return new
    else:
        return generate_subgroup(new)

def DyerN(w):
    W = w.parent()
    return [t for t in W.reflections() if (t*w).length() < w.length()]

def DyerCoxeterGenerators(H):
    return [w for w in H if set(DyerN(w)) == set([w])]
