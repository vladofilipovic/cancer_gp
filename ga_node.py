"""
The :mod:`ga-node` module contains GaNodeInfo and GaNode classes.

GaNode class is an node of the mutation tree to be build and evaluated.
"""

import random

from anytree import NodeMixin, RenderTree, PostOrderIter
from bitstring import BitArray

from collection_helpers import count, index_of, last_index_of
from read_element import ReadElement

class GaNodeInfo(object):
    """
    Information about nodes of the GA Tree.
    """
    typeDescription = "GaNodeInfo"


class GaNode(GaNodeInfo, NodeMixin): 
    """
    Node of the GA tree.
    """
    
    def __init__(self, node_label, binary_tag, parent=None):
        """
        Instance initialization.
        """
        super(GaNodeInfo, self).__init__()
        self.node_label = node_label
        self.binary_tag = binary_tag
        self.parent = parent

    def __repr__(self):
        """
        Obtaining representation of the instance.
        """
        ret = ""
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s " % (pre, node.node_label)
            ret += treestr.ljust( 10 ) + node.binary_tag.bin + '\n'
        return ret
    
    def __str__(self):
        """
        Obtaining string representation of the instance.
        """
        ret = ""
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s " % (pre, node.node_label)
            ret += treestr.ljust( 10 ) + node.binary_tag.bin + '\n'
        return ret
    
    def tree_print( self, endS = '\n'):
        """
        Function for printing GA tree.
        """
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s " % (pre, node.node_label)
            print(treestr.ljust( 10 ), node.binary_tag.bin )
        print(end=endS)
        return
    
    def attach_child( self, child):
        """
        Function for adding child GA node.
        """
        child.parent = self
        return

    def flip_node_label(self):
        """
        Flipping the label of the node.
        """
        self.node_label = self.node_label.strip()
        if(self.node_label.endswith('+')):
            self.node_label = self.node_label[:-1] + '-'
        elif(self.node_label.endswith('-')): 
            self.node_label = self.node_label[:-1] + '+'
        return

    def tree_initialize(self, labels, size):
        """
        Initialization od the tree.
        """
        current_tree_size = 1
        probability_of_node_creation = 0.9
        for i in range( 2 * size ):
               if( random.random() < probability_of_node_creation):
                   # create new leaf node
                   label_to_insert = random.choice( labels ) + '+'
                   leaf_bit_array = BitArray()
                   leaf = GaNode(label_to_insert, leaf_bit_array)
                   # find the parent of the leaf node
                   position = random.randint(0, current_tree_size)
                   if( position == 0):
                       parent_of_leaf = self
                   else:
                       j = 1
                       for node in PostOrderIter(self):
                           if( j== position):
                               parent_of_leaf = node
                               break
                           else:
                               j += 1    
                   # attach leaf node
                   parent_of_leaf.attach_child(leaf)
                   # reverse node label, if necessary
                   node = leaf.parent
                   while( node.parent != None):
                       if( leaf.node_label == node.node_label):
                           leaf.flip_node_label()
                           break
                       if( leaf.node_label[:-1] == node.node_label[:-1]):
                           break
                       node = node.parent
                   current_tree_size += 1 
                   # delete leaf is label is duplicate within siblings
                   for node in leaf.parent.children:
                       if( node.node_label == leaf.node_label and node != leaf):
                           leaf.parent = None;
                           current_tree_size -= 1
                           break
               if( i > size ):
                    probability_of_node_creation *= 0.7
        self.tree_compress_vertical()
        self.tree_compress_horizontal()
        self.tree_set_binary_tags(labels)
        return
      
    def tree_compress_horizontal(self):
        """
        Horizontal compression od the tree.
        """
        print( "Tree Compress horizontal" )
        return
        
    def tree_compress_vertical(self):
        """
        Vertical compression od the tree.
        """
        print( "Tree Compress vertical" )
        #for n in self.children:
        #    for c in n.children:
        #        if( n.node_label[:-1] == c.node_label[:-1]):
        #            for x in c.children:
        #                x.parent = self
        #for n1 in self.children:
        #    for n2 in self.children:
        #        if n1.node_label == n2.node_label and n1!=n2:
        #            n2.parent = None
        #            for c in n2.children:
        #                c.parent = n1  
        #for n in self.children:
        #     n.compressTree()
        return
 
    def children_set_binary_tags(self, labels):
        """
        Set binary tag of all children according to label.
        """
        for node in self.children:
            node.binary_tag.append( self.binary_tag )
            current_label = node.node_label.strip()
            bit = -1
            if(current_label.endswith('+')):
                bit = 1
                current_label = current_label[:-1]
            elif(current_label.endswith('-')): 
                bit = 0
                current_label = current_label[:-1]
            if( bit != 1 and bit != 0):
                continue
            i = labels.index(current_label)
            if( i == -1):
                continue
            node.binary_tag[i] = bit
        return

    def tree_set_binary_tags(self, labels):
        """
        Set binary tag of all descendants according to node label.
        """
        self.children_set_binary_tags(labels)
        for node in self.children:
            node.tree_set_binary_tags(labels)
        return

    def children_set_binary_tags_hamming(self):
        """
        Set binary tag of all children according to Hamming distances.
        """
        last_pos_of_one= last_index_of( self.binary_tag, True)
        if( last_pos_of_one == -1):
            last_pos_of_one = 0
        i = last_pos_of_one +1
        for node in self.children:
            node.binary_tag.append( self.binary_tag )
            node.binary_tag.invert(i)
            i = i+1
        return

    def tree_set_binary_tags_hamming(self):
        """
        Set binary tag of all descendants according to Hamming distances.
        """
        self.children_set_binary_tags_hamming()
        for node in self.children:
            node.tree_set_binary_tags_hamming()
        return
    
    def closest_node_in_tree( self, read ):
        """
        Finds the closest node in the tree for the given read.
        """
        closest = self
        closest_bit_array = self.binary_tag ^ read.binary_read 
        closest_distance = closest_bit_array.count(True)
        for node in PostOrderIter(self):
            current_bit_array = node.binary_tag ^ read.binary_read
            current_distance = current_bit_array.count(True)
            if( current_distance < closest_distance):
                closest = node
                closest_bit_array = current_bit_array
                closest_distance = current_distance
        return (closest, closest_distance)



def assign_reads_to_tree( root, reads):
    """
    Assigns all the reads to the closest nodes in the tree,
    respectively.
    """
    total_distance = 0
    complete_assignment = {}
    for read in reads:
        (node, d) = root.closest_node_in_tree( read )
        complete_assignment[read] = node
        total_distance += d
    return (complete_assignment, total_distance)    
    
    
def init_ga_node_individual(ind_class, labels, size):
    """
    Initialization of the individual.
    """
    rootBitArray = BitArray(int = 0, length = len(labels) )
    root = ind_class('--', rootBitArray)
    root.tree_initialize(labels, size)
    return root

def evaluation_ga_node(reads, individual):
    """
    evaluation of the individual.
    """
    objection_value = 0
    for read in reads:
        (node, d) = individual.closest_node_in_tree( read )
        objection_value += d
    return (objection_value,)    

def crossover_ga_node(individual1, individual2):
    """
    Crossover between individual1 and individual2.
    """
    print( "In crossover" )
    return (individual1, individual2)

def mutation_ga_node(individual):
    """
    Mutatuion of the individual.
    """
    print( "In mutation" )
    #randomIndex = random.choice(individual.children)
    return (individual,)
