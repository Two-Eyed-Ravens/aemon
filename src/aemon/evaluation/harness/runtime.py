"""Fail-closed checks of reported identity; receipts remain operator evidence."""

from __future__ import annotations

import hashlib
import json
import urllib.request
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from aemon.agent.backends.llama_client import headers
from aemon.common.types import Json, LoraSetting


class RuntimeExpectation(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, strict=True)

    model_path: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    context: int = Field(gt=0)
    build_info: str = Field(min_length=1)
    template_sha256: str = Field(pattern=r'^[a-f0-9]{12}([a-f0-9]{52})?$')
    model_ftype: str = Field(min_length=1)
    total_slots: Literal[1] = 1
    weights_sha256: str | None = Field(default=None, pattern=r'^[a-f0-9]{64}$')


class ModelReceipt(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, strict=True)

    model_path: str = Field(min_length=1)
    sha256: str = Field(pattern=r'^[a-f0-9]{64}$')
    checked_by: str = Field(min_length=1)


class Adapter(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True, strict=True)

    id: int = Field(ge=0)
    path: str = Field(min_length=1)
    scale: float = Field(allow_inf_nan=False)


class ModelSelection(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)

    kind: Literal['base', 'merged', 'adapter'] = 'base'
    adapters: tuple[Adapter, ...] = ()


@dataclass(frozen=True)
class RuntimeIdentity:
    evidence: Json
    lora: LoraSetting


def get_metadata(url: str, endpoint: str) -> object:
    request = urllib.request.Request(url.rstrip('/') + endpoint, headers=headers())
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def adapter_setting(selection: ModelSelection, observed: object) -> LoraSetting:
    loaded = TypeAdapter(list[Adapter]).validate_python(observed)
    actual = {adapter.id: adapter.path for adapter in loaded}
    if len(actual) != len(loaded):
        raise ValueError('duplicate server adapter ids')
    if selection.kind != 'adapter':
        if selection.adapters or set(actual) - {0}:
            raise ValueError('lora=0 requires at most loaded adapter 0 and no adapter mapping')
        return 0
    chosen = {adapter.id: adapter.path for adapter in selection.adapters}
    if len(chosen) != len(selection.adapters) or not chosen or chosen != actual:
        raise ValueError('adapter mapping must name every loaded id and exact path')
    if not any(adapter.scale != 0 for adapter in selection.adapters):
        raise ValueError('adapter selection needs a nonzero scale')
    return [{'id': adapter.id, 'scale': adapter.scale} for adapter in selection.adapters]


def validate_identity(expected: RuntimeExpectation, props: Json, models: Json) -> None:
    fields = {'model_path': expected.model_path, 'build_info': expected.build_info, 'model_ftype': expected.model_ftype, 'total_slots': expected.total_slots}
    for name, value in fields.items():
        if type(props.get(name)) is not type(value) or props[name] != value:
            raise ValueError(f'runtime mismatch: {name}')
    generation = props.get('default_generation_settings')
    if not isinstance(generation, dict) or type(generation.get('n_ctx')) is not int or generation['n_ctx'] != expected.context:
        raise ValueError('runtime mismatch: context')
    template = props.get('chat_template')
    if not isinstance(template, str) or not template:
        raise ValueError('runtime missing chat_template')
    digest = hashlib.sha256(template.encode()).hexdigest()
    if not digest.startswith(expected.template_sha256):
        raise ValueError('runtime mismatch: chat_template')
    data = models.get('data')
    if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict) or data[0].get('id') != expected.model_id:
        raise ValueError('runtime mismatch: model_id')


def inspect_runtime(url: str, expected: RuntimeExpectation, selection: ModelSelection, receipt: ModelReceipt | None = None) -> RuntimeIdentity:
    props = TypeAdapter(dict[str, object]).validate_python(get_metadata(url, '/props'))
    models = TypeAdapter(dict[str, object]).validate_python(get_metadata(url, '/v1/models'))
    validate_identity(expected, props, models)
    adapters = get_metadata(url, '/lora-adapters')
    lora = adapter_setting(selection, adapters)
    if receipt is not None and (receipt.model_path != expected.model_path or receipt.sha256 != expected.weights_sha256):
        raise ValueError('operator receipt does not match expected model path/hash')
    if expected.weights_sha256 is not None and receipt is None:
        raise ValueError('expected weights hash requires an operator receipt')
    evidence = {
        'expected': expected.model_dump(mode='json'),
        'props': props,
        'models': models,
        'adapters': adapters,
        'selection': selection.model_dump(mode='json'),
        'lora': lora,
        'remote_hash_verified': False,
        'latency_scope': 'paired sequential requests, same single slot',
    }
    if receipt is not None:
        evidence['operator_receipt'] = receipt.model_dump(mode='json')
    return RuntimeIdentity(evidence, lora)
