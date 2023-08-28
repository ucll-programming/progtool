import logging

from progtool import repository, settings
from progtool.content.metadata import load_everything, load_metadata
from progtool.content.navigator import ContentNavigator
from progtool.content.tree import ContentNode, build_tree
from progtool.server.error import ServerError


class Content:
    __root: ContentNode
    __navigator: ContentNavigator

    def __init__(self, root: ContentNode, navigator: ContentNavigator):
        assert isinstance(root, ContentNode)
        self.__root = root
        self.__navigator = navigator

    @property
    def root(self) -> ContentNode:
        return self.__root

    @property
    def navigator(self) -> ContentNavigator:
        return self.__navigator


def load_content() -> Content:
    logging.info("Loading content...")
    root_path = settings.repository_exercise_root()

    logging.info("Loading metadata")
    # TODO Add tag filtering functionality
    metadata = load_metadata(root_path, link_predicate=load_everything(force_all=True))

    if metadata is None:
        raise ServerError("No content found!")

    logging.info("Building tree")
    tree = build_tree(metadata)

    logging.info("Building navigator")
    navigator = ContentNavigator(tree)

    logging.info("Done reading content")
    return Content(tree, navigator)
