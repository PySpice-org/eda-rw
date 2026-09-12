
####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['LibreSexpr', 'UuidSexpr']

####################################################################################################

from collections.abc import Callable

from rich import print

from edarw.geometry import Position
from edarw.sexpr import UUID, Positional, SexprWrapper

####################################################################################################

type PositionType = tuple[float, float]

####################################################################################################

class LibreSexpr(SexprWrapper):

    # Fixme: UuidSexpr is defined after
    _UUID_MAP: dict[UUID, dict[str, LibreSexpr]] = {}

    ##############################################

    @classmethod
    def class_name(cls) -> str:
        module = cls.__module__
        i = module.rfind('.')
        assert i >= 1
        return cls.__module__[i + 1:] + '.' + cls.__name__

    ##############################################

    @classmethod
    def get_uuid(cls, uuid: UUID) -> dict[str, LibreSexpr]:
        return cls._UUID_MAP[uuid]

    @classmethod
    def get_uuid_cls(cls, uuid: UUID, class_name: str) -> LibreSexpr:
        return cls.get_uuid(uuid)[class_name]

    @classmethod
    def _register_uuid(cls, obj: UuidSexpr) -> None:
        class_name = cls.class_name()
        uuid_dict = cls._UUID_MAP.setdefault(obj.uuid, {})
        if class_name not in uuid_dict:
            uuid_dict[class_name] = obj
        else:
            # Fixme: for debugging
            # Fixme: the code create doublon instance
            obj2 = uuid_dict[class_name]
            if obj.class_name() != obj2.class_name():
                print(obj.class_name(), obj.to_json())
                print(obj2.class_name(), obj2.to_json())
                raise ValueError(f"UUID {obj.uuid}/{class_name} is not uniq")

    @classmethod
    def dump_uuids(cls) -> None:
        # print(LibreSexpr._UUID_MAP)
        for uuid, item in LibreSexpr._UUID_MAP.items():
            if len(item) > 1:
                print(item)

    ##############################################

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        def make_uuid_getter(field: str) -> Callable:
            def wrapper(self: LibreSexpr) -> dict[str, LibreSexpr] | SexprWrapper | None:
                uuid = getattr(self, field)
                if uuid is None:
                    return None
                uuid_dict = self.get_uuid(uuid)
                if len(uuid_dict) == 1:
                    return list(uuid_dict.values()).pop()
                return uuid_dict
            return wrapper

        def position_getter(self: LibreSexpr) -> Position:
            return Position(*self.position)  # ty: ignore[unresolved-attribute]

        for field, type_ in cls._annotations().items():
            # Fixme: UUID is a TypeAliasType
            # match type_:
            #     case UUID():
            if type_ == UUID:
                setattr(cls, f'{field}_obj', property(make_uuid_getter(field)))
            match field:
                case 'position':
                    setattr(cls, f'position_obj', property(position_getter))
            #     is_list = cls._is_list_type(type_)

    ##############################################

    def __repr__(self) -> str:
        return self.class_name()

####################################################################################################

class UuidSexpr(LibreSexpr):
    uuid: Positional[UUID]

    ##############################################

    def __init__(self, sexpr: list, indent_level: int = 0, parent: object | None = None) -> None:
        super().__init__(sexpr, indent_level, parent)
        self._register_uuid(self)

    ##############################################

    def __repr__(self) -> str:
        return f"{self.class_name()} {self.uuid}"
