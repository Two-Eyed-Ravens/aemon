"""The candidate boundary accepts data selecting reviewed recovery mechanisms."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Feature = Literal['resample_repeats', 'mask_rereads', 'progress', 'budget', 'citations', 'no_repeats', 'quote_menu', 'grounded_beliefs', 'evidence_first']


class Candidate(BaseModel):
    """Immutable, bounded input to the trusted runner."""

    model_config = ConfigDict(extra='forbid', frozen=True)

    version: Literal[1] = 1
    name: str = Field(min_length=1, max_length=64, pattern=r'^[a-z][a-z0-9_-]*$')
    features: tuple[Feature, ...] = ()

    @field_validator('features')
    @classmethod
    def validate_features(cls, features: tuple[Feature, ...]) -> tuple[Feature, ...]:
        if len(set(features)) != len(features):
            raise ValueError('features must be unique')
        if 'evidence_first' in features and 'quote_menu' not in features:
            raise ValueError('evidence_first requires quote_menu')
        return tuple(sorted(features))

    def digest(self) -> str:
        encoded = self.model_dump_json().encode()
        return hashlib.sha256(encoded).hexdigest()


def load_candidate(path: Path) -> Candidate:
    with path.open() as stream:
        return Candidate.model_validate_json(stream.read())
