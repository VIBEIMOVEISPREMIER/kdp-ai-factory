from dataclasses import asdict
from ..domain import BookSpec
def to_dict(spec: BookSpec): return asdict(spec)
