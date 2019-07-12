from collections import OrderedDict


class AppImageData(OrderedDict):
    def __init__(self, name='', value='', parent=None):
        super(AppImageData, self).__init__()
        self.name = name
        self.value = value
        self.parent = parent

    def __str__(self):
        return f'{self.name}: {super().__str__()}'

    def __repr__(self):
        return f'{self.name}: {super().__repr__()}'

    def set_key(self, key, value):
        levels = key.split('/')
        item = self
        for level in levels:
            if item.get(level) is None:
                item[level] = AppImageData(name=level)
            item = item[level]
        item.value = value

    def get_key(self, key):
        levels = key.split('/')
        item = self
        for level in levels:
            item = item.get(level)
            if item is None:
                return None
        return item

    @staticmethod
    def from_dict(dict_, name):
        def create_data_item(key, value):
            item = AppImageData(name=key)
            if isinstance(value, dict):
                for k, v in value.items():
                    child = create_data_item(k, v)
                    child.parent = item
                    item[k] = child
            else:
                item.value = value
            return item

        return create_data_item(name, dict_)


class AppImageDataWalker:
    """
    The walker performs a breath first search on the given item. The behavior
    can be changed by supplying the optional dfs parameter to depth first search.
    """

    def __init__(self, item, dfs=False):
        self.item = item
        self.dfs = dfs

    @staticmethod
    def _walk(item, dfs):
        # if item is None:
        #     return
        if not dfs:
            yield item
        for child in item.values():
            for walked in AppImageDataWalker._walk(child, dfs):
                yield walked
        if dfs:
            yield item

    def __iter__(self):
        return AppImageDataWalker._walk(self.item, self.dfs)
