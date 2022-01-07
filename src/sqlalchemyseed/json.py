from typing import Any, List, Union
from dataclasses import dataclass


class JsonWalker:
    """
    JsonWalker class
    """

    def __init__(self, json: Union[list, dict] = None) -> None:
        self.path = []
        self.root = json
        self.current = json

    @property
    def current_key(self):
        """
        Returns the key of the current json
        """
        return self.path[-1]

    def forward(self, keys: List[Union[int, str]]):
        """
        Move and replace current json forward.
        Returns current json.
        """
        self.current = self.find_from_current(keys)
        self.path.extend(keys)
        return self.current

    def backward(self):
        """
        Revert current json to its parent.
        Returns reverted current json
        """
        if len(self.path) == 0:
            raise ValueError('No parent found error')

        self.current = self.find_from_root(self.path[:-1])
        self.path.pop()

    def find_from_current(self, keys: List[Union[int, str]]):
        """
        Find item from current json that correlates list of keys
        """
        return self._find(self.current, keys)

    def _find(self, json: Union[list, dict], keys: List[Union[int, str]]):
        """
        Recursive call of finding item
        """
        return self._find(json[keys[0]], keys[1:]) if keys else json

    def find_from_root(self, keys: List[Union[int, str]]):
        """
        Find item from the root json that correlates list of keys
        """
        return self._find(self.root, keys)

    def reset(self, root=None):
        """
        Resets to initial state.
        If root argument is supplied, self.root will be replaced.
        """
        if root is not None:
            self.root = root

        self.current = self.root
        self.path.clear()

    def iter_as_list(self):
        """
        Iterates current as list.
        Yiels value.

        If current is not a list, then it only yields the current value.
        Forward method will not be called.
        """
        if not self.is_list:
            yield self.current
            return  # exit method

        current = self.current
        for index, value in enumerate(current):
            self.forward([index])
            yield value
            self.backward()

    def iter_as_dict_items(self):
        """
        Iterates current as dict.
        Yields key and value.
        Nothing will be yielded if curent is not dict
        """
        if not self.is_dict:
            return

        current = self.current
        for key, value in current.items():
            self.forward([key])
            yield key, value
            self.backward()

    @property
    def is_dict(self):
        """
        Returns true if current json is dict
        """
        return isinstance(self.current, dict)

    @property
    def is_list(self):
        """
        Returns true if current json is list
        """
        return isinstance(self.current, list)


@dataclass(frozen=True)
class JsonKey:
    """
    JsonKey data class for specifying type of the key its value holds.
    """
    key: str
    type_: Any
