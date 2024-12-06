import dataclasses as dc

from interpreter import objects


@dc.dataclass
class Environment:
    store: dict[str, objects.Object] = dc.field(init=False, default_factory=dict)

    def get(self, name: str) -> tuple[objects.Object | None, bool]:
        try:
            return self.store[name], True
        except KeyError:
            return None, False

    def set(self, name: str, obj: objects.Object) -> objects.Object:
        self.store[name] = obj
        return obj
