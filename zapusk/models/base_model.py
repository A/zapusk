from dataclasses import fields
import inspect


class BaseModel:
    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, type(self)):
            for fld in fields(self):  # type: ignore
                left = getattr(self, fld.name)
                right = getattr(value, fld.name)

                if left != right:
                    return False

            return True
        if isinstance(value, dict):
            for fld in fields(self):  # type: ignore
                left = getattr(self, fld.name)
                right = value.get(fld.name)

                if left != right:
                    return False

            return True

        return False

    @classmethod
    def from_dict(cls, env):
        return cls(
            **{k: v for k, v in env.items() if k in inspect.signature(cls).parameters}
        )
