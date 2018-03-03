# -*- coding: utf-8 -*-
r"""
uhw_modules

This module contains the cones of unitarizabhle
highest weights and implementation of Enright's
formula for their nilpotent cohomology.

EXAMPLES ::

    sage: from uhw_modules import HermitianSymmetriPair as HSP
    sage: HSP(["A", 4], index_set=[1,2,3])
    Hermitian Symmetric Pair of type A_4 [1,2,3]

REFERENCES:

.. [DES] Davidson, Enright, Stanke
   *Differential Operators and Highest Weight Representations*
    Memoirs of the American Mathematical Society, 1991.
    
.. [E] Enright
   *Analogues of Kostant's u-cohomology formulas for unitary highest modules*
   Journal für die reine und angewandte Mathematik 392, 1988.

AUTHORS:

- Vít Tuček: initial implementation
"""
from sage.misc.cachefunc import cached_method
from sage.modules.free_module_element import vector
from sage.misc.abstract_method import abstract_method
from sage.combinat.root_system.root_system import RootSystem
from sage.combinat.root_system.weyl_group import WeylGroup
from uhw_utils import RootSystemFacets, get_length_function, WG_action, generate_subgroup


class ParabolicPair:
    """
    Class that represents a complex parabolic pair(G,P), where G is a complex (semi?)simple Lie group and P its parabolic subgroup.
    This pair is encoded as RootSystem for G and index set of those simple roots that belong to the Levi part of P.
    """

    def __init__(self, cartan_type, index_set):
        self.cartan_type = cartan_type
        self.root_system = RootSystem(cartan_type)
        self.index_set = index_set  # TODO add checks so that index_set is a subset of the set indexing simple roots
        self.weyl_group = WeylGroup(cartan_type)
        self.ambient_space = self.weyl_group.domain()
        self.rho = self.ambient_space.rho()
        self.root_poset = self.ambient_space.root_poset(facade=True)
        self.root_lattice = self.ambient_space.root_system.root_lattice()
        self.nonparabolic_roots = [x.to_ambient() for x in
                                   self.root_lattice.positive_roots_nonparabolic(index_set=index_set)]
        self.nonparabolic_root_poset = self.root_poset.subposet(self.nonparabolic_roots)

    @cached_method
    def get_root_system_facets(self):
        return RootSystemFacets(self.cartan_type)

    def symbolic_weight_poset(self, cone, weyl_group_poset):
        """
        Returns a poset of weights with symbolic coordinates given by action of weyl_group_poset on the vertex of the cone. 
        The symbolic coordinates parametrize the interior of the cone even if the weyl_group_poset is valid only on a subpolyhedron. 
        This way it is easier to compare cohomology for different subpolyhedra.
        """
        pass

    def kostant_cohomology(self, v):
        """
        Calculates cohomology of nilpotent radical of the Lie algebra of P with values in a g-dominant and g-integral weight v using Kostant's formula
        Returns minimal length representatives of Weyl group elements organized into a poset.
        """
        pass

    def get_poset_from_embedding(self, poset, embedding):
        """
        Creates a poset of Weyl group elements of self through mapping via embedding from another poset. Used for relative BGG and Enright-Shelton equivalence.
        :embedding:  is a mapping of simple roots in some other Weyl group into reflections of self.weyl_group implemented via a dictionary indexed by numbers
        """

        # # TODO why is this here exactly?
        # for i in embedding.keys():
        #     embedding[i] = self.ambient_space.from_vector(vector(embedding[i]))

        #       reflections = w.parent().reflections()
        #       embedding = {}
        #       for i  in embedding:
        #           embedding[i] = reflections()[embedding[i]]
        def embedd(w):
            reflections_word = map(lambda j: embedding[j], w.reduced_word())
            return self.weyl_group.from_reduced_word(reflections_word, word_type="all")

        # print "Embedding: ", embedding
        return poset.relabel(embedd)

    def relative_bgg(self, other_index_set=None):
        """
        TODO
        Have to figure appropriate API first.
        """
        pass


class HermitianSymmetricPair(ParabolicPair):

    def get_generating_roots(self, v):
        """
        Returns a list of roots that generate the reflection subgroup which governs cohomology of unitarizable hihgest weight modules.
        First part of Enright's formula from his paper on u-cohomology.
        The convention is that Verma modules are induced from lambda (i.e. no rho-shift)
        """
        Psi = [r for r in self.ambient_space.positive_roots() if r.scalar(self.rho + v) == 0]

        if self.ambient_space.cartan_type()[0] in "BCG":
            print [x.is_short_root() for x in Psi]
            is_there_long_root = any(not (x.is_short_root()) for x in Psi)
        else:
            is_there_long_root = False
        print "Is there long root:", is_there_long_root

        def test_root(r):
            n = r.associated_coroot().scalar(v + self.rho)  # TODO check coroot calculations
            if is_there_long_root:
                short = r.is_short_root()
            else:
                short = True
            # print r, long_root, short
            return n.is_integer() and n > 0 and short

        nonparabolic_roots = [x.to_ambient() for x in
                              self.ambient_space.root_system.root_lattice().positive_roots_nonparabolic(index_set=self.index_set)]
        parabolic_roots = [x.to_ambient() for x in
                           self.ambient_space.root_system.root_lattice().positive_roots_parabolic(index_set=self.index_set)]
        # print("Nonparabolic roots: %s" % sorted(nonparabolic_roots))
        Phi = [r for r in nonparabolic_roots if test_root(r) and all(r.scalar(s) == 0 for s in Psi)]
        return Phi, Psi, parabolic_roots, nonparabolic_roots

    def get_subsystem_data(self, v, debug=True):
        # This should work with self.AS and self.W no?
        #AS = v.parent()
        #W = AS.weyl_group()
        generating_roots, Psi, parabolic_roots, nonparabolic_roots = self.get_generating_roots(v)
        reflections = self.weyl_group.reflections()
        generators = set(reflections[r] for r in generating_roots)

        if debug:
            print("Generating subgroup from %d generators" % len(generators))

        # W_lambda = [W.element_class(W, h) for h in W.subgroup(generators)] # too slow
        if self.ambient_space.rank() < 6:  # BUG gap is exceptionally slow for larger rank
            W_lambda = self.weyl_group.subgroup(generators)
        else:
            W_lambda = list(generate_subgroup(
                generators))  # subgroup generates H as a matrix group and we lose all the WeylGroupElement methods # too slow
        if debug:
            print("The generated subgroup has %d elements" % len(W_lambda))
        W_lambda_reflections = []
        for x in W_lambda:
            g = self.weyl_group.element_class(self.weyl_group, x)
            if g in reflections:
                W_lambda_reflections.append(g)

        if debug:
            print("The subgroup has %d reflections" % len(W_lambda_reflections))

        # calculate Coxeter generators of the reflection subgroup
        # see [Deodhar] or [Dyer] for proof
        def DyerCoxeterGenerators(H_reflections):
            # optimized version
            # H_reflections = [W.element_class(W, x) for x in reflections if x in H] # WARNING switching H and reflections leads to empty set!
            # H_reflections = [W.element_class(W, x) for x in H if W.element_class(W, x) in reflections] # the previous stopped working in Sage 7.6 # refactored shortly thereafter to assume that we have only reflections at input
            W_length = get_length_function(self.ambient_space.positive_roots())

            def DyerN(w):
                w = self.weyl_group.element_class(self.weyl_group, w)
                return set(t for t in H_reflections if W_length(t * w) < W_length(w))

            return [w for w in H_reflections if DyerN(w) == {w}]

        coxeter_generators = DyerCoxeterGenerators(W_lambda_reflections)

        lambda_positive_roots = [r for r in reflections.keys() if reflections[r] in W_lambda_reflections]
        lambda_simple_roots = [r for r in reflections.keys() if reflections[r] in coxeter_generators]
        lambda_parabolic_roots = [r for r in lambda_positive_roots if r in parabolic_roots]
        lambda_nonparabolic_roots = [r for r in lambda_positive_roots if r in nonparabolic_roots]

        # decompose coset representative according to their length
        from collections import defaultdict
        def is_dominant(v, positive_roots):
            return all(v.scalar(r) > 0 for r in positive_roots)

        lambda_W_c = defaultdict(list)
        lambda_length = get_length_function(lambda_positive_roots)
        for w in W_lambda:
            if is_dominant(WG_action(w, self.rho), lambda_parabolic_roots):
                lambda_W_c[lambda_length(w)].append(w)

        return Psi, generating_roots, lambda_simple_roots, lambda_positive_roots, lambda_parabolic_roots, lambda_nonparabolic_roots, W_lambda, lambda_W_c

    def enright_cohomology(self, v):
        """
        Calculates cohomology of nilpotent radical of the Lie algebra of P with values in a unitarizable highest weight module using Enright's formula.
        """
        pass

    @abstract_method
    def uhw_cones(self):
        """
        Returns list of cones of highest weights of highest weight unitarizable modules.
        """
        pass
