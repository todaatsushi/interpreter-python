from __future__ import annotations


import dataclasses as dc

from monkey.interpreter import objects


@dc.dataclass
class Environment:
    store: dict[str, objects.Object] = dc.field(init=False, default_factory=dict)
    outer: Environment | None = None

    def get(self, name: str) -> tuple[objects.Object | None, bool]:
        try:
            return self.store[name], True
        except KeyError:
            pass

        if self.outer:
            return self.outer.get(name)
        return None, False

    def set(self, name: str, obj: objects.Object) -> objects.Object:
        self.store[name] = obj
        return obj

    @classmethod
    def new_enclosed(cls, env: Environment) -> Environment:
        return cls(outer=env)
