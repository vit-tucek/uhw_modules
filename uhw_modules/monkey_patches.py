
######################################################################
##############  Parabolic enhancements for Weyl groups  ##############
######################################################################

import sage.combinat.root_system.weyl_group as wg

def parabolic_bruhat_graph(self, index_set = None, side="right"):
    """
    Returns the Hasse graph of the poset ``self.bruhat_poset(index_set,side)`` with edges labeled by the cover relation
    """
    elements = self.minimal_representatives(index_set, side)
    covers =[(x,y)  for y in elements for x in y.bruhat_lower_covers() if x in elements]
    res = DiGraph()
    for u,v in covers:
        res.add_edge(u,v,v.inverse()*u)
    return res

def parabolic_weight_graph(self, weight, index_set=None,side="right"):
    elements = self.minimal_representatives(index_set,side)
    #wl0 = self.long_element(index_set)
    #covers =[(wl0*x,wl0*y)  for y in elements for x in y.bruhat_lower_covers() if x in elements] # funguje jen pro "right"
    covers =[(x,y)  for y in elements for x in y.bruhat_lower_covers() if x in elements]
    res = DiGraph()
    rho = weight.parent().rho()
    v = weight + rho
    def act_on_weight(v,x):
        return str((v.weyl_action(x) - rho).to_dominant_chamber(index_set).to_vector())
    for x,y in covers:
        #a = v.weyl_action(x) - rho
        #b = v.weyl_action(y) - rho
        #res.add_edge(str(a.to_vector()),str(b.to_vector()))
        a = act_on_weight(v,x)
        b = act_on_weight(v,y)
        res.add_edge(a,b)
    return res

def parabolic_weight_graph_enum(self, weight, index_set=None, side="right"):
    elements = [x for x in enumerate(self.minimal_representatives(index_set,side))]
    covers =[(x,y)  for y in elements for x in elements if x[1] in y[1].bruhat_lower_covers()]
    res = DiGraph()
    rho = weight.parent().rho()
    v = weight + rho
    def act_on_weight(v,x):
        return str((v.weyl_action(x) - rho).to_dominant_chamber(index_set).to_vector())
    for x,y in covers:
        a = str(x[0]) + ":" + act_on_weight(v,x[1])
        b = str(y[0]) + ":" + act_on_weight(v,y[1])
        res.add_edge(a,b)
    return res

def parabolic_poset(self, levi_indices, side="right"):
    # returns a poset of minimal representatives of W_S \ W
    # self is a finite-dimensional Weyl group
    # first we compute orbit of the characteristic vector of our parabolic subalgebra
    # this is for representatives of left cosets; to obtain representatives for right cosets just take the inverse
    elements = self.minimal_representatives(levi_indices, side)
    #since our Weyl elements should be already reduced (?), we could optimize this step by constructing the cover relations directly thus reducing quadratic complexity to linear
    covers = tuple([x,y]  for y in elements for x in y.bruhat_lower_covers() if x in elements)
    return Poset( (elements, covers), cover_relations = True)

def parabolic_weight_poset(self, weight, levi_indices, side="right", relative_index_set=None):
    rho = weight.parent().rho()
    v = weight + rho
    elements = self.minimal_representatives(levi_indices, side, relative_index_set=relative_index_set)
    covers = tuple([x,y]  for y in elements for x in y.bruhat_lower_covers() if x in elements)
    labels = {}
    for x in elements:
        labels[x] = str((v.weyl_action(x) - rho).to_dominant_chamber(levi_indices).to_vector())
    return Poset( (elements, covers), cover_relations = True, element_labels=labels)

def minimal_representatives(self, index_set=None, side="right", relative_index_set=None):
    """
    Returns the set of minimal coset representatives of ``self`` by a parabolic subgroup.

    INPUT:

    - ``index_set`` - a subset (or iterable) of the nodes of the Dynkin diagram, empty by default, denotes the generators of the Levi part
    - ``side`` - 'left' or 'right' (default)
    - ``relative_index_set`` - superset of index_set for the relative Case, again determines the Levi part

    See documentation of ``self.bruhat_poset`` for more details.

    The output is equivalent to ``set(w.coset_representative(index_set,side))``

    but this routine is much faster. For explanation of the algorithm see e.g. Cap, Slovak:
    Parabolic geometries, p. 332

    EXAMPLES::

        sage: G = WeylGroup(CartanType("A4"),prefix="s")
        sage: index_set = [1,3,4]
        sage: side = "left"
        sage: a = set(w for w in G.minimal_representatives(index_set,side))
        sage: b = set(w.coset_representative(index_set,side) for w in G)
        sage: print a.difference(b)
        set([])
    """
    from sage.combinat.root_system.root_system import RootSystem
    from copy import copy

    if side != 'right' and side != 'left':
        raise ValueError, "%s is neither 'right' nor 'left'" % side

   #TODO check for relative_index_set being a superset of index_set

    weight_space = RootSystem(self.cartan_type()).weight_space()
    if index_set is None:
        crossed_nodes = set(self.index_set())
        relative_crossed_nodes = set()
    else:
        crossed_nodes = set(self.index_set()).difference(index_set)
        if not relative_index_set:
            relative_index_set = self.index_set()
        relative_crossed_nodes = set(self.index_set()).difference(relative_index_set)
    # the characteristic vector
    rhop = sum([weight_space.fundamental_weight(i) for i in crossed_nodes if not(i in relative_crossed_nodes)])
    '''

    The variable "todo" serves for traversing the orbit of rhop, while the directory "known" serves
elements in the orbit of rhop while known[vec] are paths of simple reflections from rhop to vec.

    '''
    todo = [rhop]
    known = dict()
    known[rhop] = []
    if rhop == 0:
        return {self.one()}
    else:
        while len(todo) > 0:
            vec = todo.pop()
            nonzero_coeffs = [i for i in self.index_set() if (vec.coefficient(i) > 0) and (i in relative_index_set)]
            for i in nonzero_coeffs:
                new_vec = vec.simple_reflection(i)
                new_reflections = copy(known[vec])
                new_reflections.append(i)
                todo.append(new_vec)
                known[new_vec] = new_reflections
        if side =='left':
            return set(self.from_reduced_word(w) for w in known.values())
        else:
            #here we could just take the inverses of w but reversing the list of simple reflections
            return set(self.from_reduced_word(w[::-1]) for w in known.values())

def bruhat_poset(self, index_set = None, side="right", facade = False):
    from sage.combinat.posets.posets import Poset
    elements = self.minimal_representatives(index_set, side)
    # Since our Weyl elements should be already reduced (?), we could
    # optimize this step by constructing the cover relations directly (see Cap, Slovak: Parabolic
    # thus reducing quadratic complexity of the next step to linear. On the other hand, we would
    covers = tuple([x,y] for y in elements for x in  y.bruhat_lower_covers()
                    if x in elements)
    return Poset((self, covers), cover_relations = True, facade=facade)

def reflection_subgroup(self, generators):
    """
    Returns subgroup generated by `generators` as a Weyl group.
    """
    pass

wg.WeylGroup_gens.minimal_representatives = minimal_representatives
#wg.WeylGroup_gens.bruhat_poset = bruhat_poset
wg.WeylGroup_gens.parabolic_poset = parabolic_poset
wg.WeylGroup_gens.parabolic_bruhat_graph = parabolic_bruhat_graph
wg.WeylGroup_gens.parabolic_weight_graph = parabolic_weight_graph
wg.WeylGroup_gens.parabolic_weight_graph_enum = parabolic_weight_graph_enum
wg.WeylGroup_gens.parabolic_weight_poset = parabolic_weight_poset
wg.WeylGroup_gens.reflection_subgroup = reflection_subgroup

# small hack for LaTeXing DynkinDiagrams of generalized flag manifolds
from sage.combinat.root_system.cartan_type import CartanType_abstract as cta
def _my_latex_draw_node(self, x, y, label, position="below=4pt", fill='white'):
        r"""
        Draw (possibly marked [crossed out]) circular node ``i`` at the
        position ``(x,y)`` with node label ``label`` .
        - ``position`` -- position of the label relative to the node
        - ``anchor`` -- (optional) the anchor point for the label
        EXAMPLES::
            sage: CartanType(['A',3])._latex_draw_node(0, 0, 1)
            '\\draw[fill=white] (0 cm, 0 cm) circle (.25cm) node[below=4pt]{$1$};\n'
        """
        global parabolic_index_set
        #print parabolic_index_set, label
        fill = "black" if label in parabolic_index_set else "white"
        return "\\draw[fill={}] ({} cm, {} cm) circle (.1cm) node[{}]{{${}$}};\n".format(fill, x, y, position, label)
cta._latex_draw_node =  _my_latex_draw_node


