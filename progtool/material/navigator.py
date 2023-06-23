from typing import Callable, Iterator, Literal, Optional
from progtool.material.tree import MaterialTreeBranch, MaterialTreeLeaf, MaterialTreeNode, Section, Exercise, Explanation
import logging


class MaterialNavigator:
    __nodes: list[MaterialTreeNode]

    __node_index_map: dict[MaterialTreeNode, int]

    def __init__(self, root: MaterialTreeNode):
        self.__nodes = list(root.preorder_traversal())
        self.__node_index_map = {node: index for index, node in enumerate(self.__nodes)}

    def find_successor_leaf(self, node: MaterialTreeNode) -> Optional[MaterialTreeNode]:
        """
        Given any node, find the first *leaf* that appears after it in preorder traversal.
        """
        assert node in self.__node_index_map, "BUG: All nodes should occur in __node_index_map"
        start_index = self.__node_index_map[node] + 1
        return self.__search_preorder_traversal(
            start_index,
            1,
            lambda node: isinstance(node, MaterialTreeLeaf)
        )

    def find_predecessor_leaf(self, node: MaterialTreeNode) -> Optional[MaterialTreeNode]:
        """
        Given any node, find the first *leaf* that appears before it in preorder traversal.
        """
        assert node in self.__node_index_map, "BUG: All nodes should occur in __node_index_map"
        start_index = self.__node_index_map[node] - 1
        return self.__search_preorder_traversal(
            start_index,
            -1,
            lambda node: isinstance(node, MaterialTreeLeaf)
        )

    def find_predecessor_branch(self, node: MaterialTreeNode) -> Optional[MaterialTreeNode]:
        """
        Given any node, find the first *branch* that appears before it in preorder traversal.
        This is equivalent with looking for the parent branch node.
        """
        assert node in self.__node_index_map, "BUG: All nodes should occur in __node_index_map"
        start_index = self.__node_index_map[node] - 1
        return self.__search_preorder_traversal(
            start_index,
            -1,
            lambda node: isinstance(node, MaterialTreeBranch)
        )

    def __search_preorder_traversal(self, start_index: int, direction: Literal[-1, 1], predicate: Callable[[MaterialTreeNode], bool]) -> Optional[MaterialTreeNode]:
        index = start_index
        while 0 <= index < len(self.__nodes) and not predicate(self.__nodes[index]):
            index += direction
        if 0 <= index < len(self.__nodes):
            return self.__nodes[index]
        else:
            return None
