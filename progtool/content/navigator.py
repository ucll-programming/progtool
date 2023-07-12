from typing import Callable, Iterator, Literal, Optional
from progtool.content.tree import ContentTreeBranch, ContentTreeLeaf, ContentNode, Section, Exercise, Explanation
import logging


class ContentNavigator:
    __nodes: list[ContentNode]

    __node_index_map: dict[ContentNode, int]

    __parent_mapping: dict[ContentNode, ContentTreeBranch]

    def __init__(self, root: ContentNode):
        self.__nodes = list(root.preorder_traversal())
        self.__node_index_map = {node: index for index, node in enumerate(self.__nodes)}
        self.__parent_mapping = {}
        root.build_parent_mapping(self.__parent_mapping)

    def find_successor_leaf(self, node: ContentNode) -> Optional[ContentNode]:
        """
        Given any node, find the first *leaf* that appears after it in preorder traversal.
        """
        assert node in self.__node_index_map, "BUG: All nodes should occur in __node_index_map"
        start_index = self.__node_index_map[node] + 1
        return self.__search_preorder_traversal(
            start_index,
            1,
            lambda node: isinstance(node, ContentTreeLeaf)
        )

    def find_predecessor_leaf(self, node: ContentNode) -> Optional[ContentNode]:
        """
        Given any node, find the first *leaf* that appears before it in preorder traversal.
        """
        assert node in self.__node_index_map, "BUG: All nodes should occur in __node_index_map"
        start_index = self.__node_index_map[node] - 1
        return self.__search_preorder_traversal(
            start_index,
            -1,
            lambda node: isinstance(node, ContentTreeLeaf)
        )

    def find_parent(self, node: ContentNode) -> Optional[ContentNode]:
        return self.__parent_mapping.get(node, None)

    def __search_preorder_traversal(self, start_index: int, direction: Literal[-1, 1], predicate: Callable[[ContentNode], bool]) -> Optional[ContentNode]:
        index = start_index
        while 0 <= index < len(self.__nodes) and not predicate(self.__nodes[index]):
            index += direction
        if 0 <= index < len(self.__nodes):
            return self.__nodes[index]
        else:
            return None
