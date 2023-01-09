import dataclasses
from typing import Callable, Optional, Tuple, Union

from flask import Response
from flask_limiter.wrappers import RequestLimit


@dataclasses.dataclass
class Limit:
    limit_value: Union[Callable[[], str], str]
    key_func: Callable[[], str]
    scope: Optional[Union[str, Callable[[str], str]]] = None
    methods: Optional[Tuple[str, ...]] = None
    error_message: Optional[str] = None
    exempt_when: Optional[Callable[[], bool]] = None
    override_defaults: Optional[bool] = False
    deduct_when: Optional[Callable[[Response], bool]] = None
    on_breach: Optional[Callable[[RequestLimit], Optional[Response]]] = None
    per_method: bool = False
    cost: Optional[Union[Callable[[], int], int]] = None
