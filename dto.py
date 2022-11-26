from dataclasses import dataclass, field
from typing import List
import numpy


@dataclass
class EntityDTO:
    id: int = None
    contour: numpy.array = None
    center_point: list = None
    entity_name: str = None
    distace: int = None
    is_enemy: bool = False
    is_character: bool = False
    is_self: bool = False
    is_targeted: bool = False


@dataclass
class EntitysDTO:
    entitys: List[EntityDTO] = field(default_factory=lambda: [])



