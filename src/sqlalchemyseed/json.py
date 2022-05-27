from typing import Callable, List, Union


class JsonWalker:
    """
    JsonWalker class
    """

    def __init__(self, json: Union[list, dict] = None) -> None:
        self.path = []
        self.root = json
        self._current = json

    @property
    def json(self):
        """
        Returns current json
        """
        return self._current

    def keys(self):
        """
        Returns list of keys either str or int
        """
        if self.json_is_dict:
            return self._current.keys()

        if self.json_is_list:
            return list(map(lambda index: index, range(len(self._current))))

        return []

    @property
    def current_key(self) -> Union[int, str]:
        """
        Returns the key of the current json
        """
        return self.path[-1]

    def forward(self, keys: List[Union[int, str]]):
        """
        Move and replace current json forward.
        Returns current json.
        """

        if len(keys) == 0:
            return self._current

        self._current = self.find_from_current(keys)
        self.path.extend(keys)
        return self._current

    def backward(self):
        """
        Revert current json to its parent.
        Returns reverted current json
        """
        if len(self.path) == 0:
            raise ValueError('No parent found error')

        self._current = self.find_from_root(self.path[:-1])
        self.path.pop()

    def find_from_current(self, keys: List[Union[int, str]]):
        """
        Find item from current json that correlates list of keys
        """
        return self._find(self._current, keys)

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

        self._current = self.root
        self.path.clear()

    def exec_func_iter(self, func: Callable):
        """
        Executes function when iterating
        """
        current = self._current
        if self.json_is_dict:
            for key in current.keys():
                self.forward([key])
                func()
                self.backward()
        elif self.json_is_list:
            for index in range(len(current)):
                self.forward([index])
                func()
                self.backward()
        else:
            func()

    def iter_as_list(self):
        """
        Iterates current as list.
        Yields index and value.

        Raises TypeError if current json is not list
        """
        if not self.json_is_list:
            raise TypeError('json is not list')

        current = self._current
        for index, value in enumerate(current):
            self.forward([index])
            yield index, value
            self.backward()

    def iter_as_dict_items(self):
        """
        Iterates current as dict.
        Yields key and value.

        Raises TypeError if current json is not dict
        """
        if not self.json_is_dict:
            raise TypeError('json is not dict')

        current = self._current
        for key, value in current.items():
            self.forward([key])
            yield key, value
            self.backward()

    @property
    def json_is_dict(self):
        """
        Returns true if current json is dict
        """
        return isinstance(self._current, dict)

    @property
    def json_is_list(self):
        """
        Returns true if current json is list
        """
        return isinstance(self._current, list)


def sort_json(json: Union[list, dict], reverse=False):
    """
    Sort json function
    """
    if isinstance(json, list):
        return sorted(sorted(sort_json(item), reverse=reverse) for item in json)

    if isinstance(json, dict):
        return {key: sort_json(value, reverse=reverse) for key, value in json.items()}

    return json
