"""
QC config dataclasses + JSON load/save/validate.
Schema is compatible with the original React app's exported qc-config.json.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


# ─── Leaf types ──────────────────────────────────────────────────────────────

@dataclass
class FilenameBlock:
    id: str
    type: str           # 'fixed' | 'wildcard' | 'list' | 'token'
    label: str
    value: str = ''     # used when type == 'fixed'
    values: List[str] = field(default_factory=list)   # used when type == 'list'
    separator: str = '_'


@dataclass
class FileTypeEntry:
    id: str
    name: str
    extension: str
    description: str = ''


@dataclass
class CodecEntry:
    id: str
    name: str
    kind: str           # 'video' | 'audio'
    aliases: List[str] = field(default_factory=list)


@dataclass
class FileTypePairEntry:
    id: str
    primaryExtension: str
    companionExtension: str
    label: str = ''


@dataclass
class NamingPatternEntry:
    id: str
    name: str
    pattern: str
    description: str = ''


# ─── Nested config containers ─────────────────────────────────────────────────

@dataclass
class CoreConfig:
    filenameBlocks: List[FilenameBlock] = field(default_factory=list)
    allowedResolutions: List[str] = field(default_factory=list)


@dataclass
class FileTypesConfig:
    entries: List[FileTypeEntry] = field(default_factory=list)


@dataclass
class CodecsConfig:
    entries: List[CodecEntry] = field(default_factory=list)


@dataclass
class FileTypePairsConfig:
    entries: List[FileTypePairEntry] = field(default_factory=list)


@dataclass
class NamingPatternsConfig:
    entries: List[NamingPatternEntry] = field(default_factory=list)


@dataclass
class ModulesConfig:
    fileTypes: FileTypesConfig = field(default_factory=FileTypesConfig)
    codecs: CodecsConfig = field(default_factory=CodecsConfig)
    fileTypePairs: FileTypePairsConfig = field(default_factory=FileTypePairsConfig)
    namingPattern: NamingPatternsConfig = field(default_factory=NamingPatternsConfig)


# ─── Root config ──────────────────────────────────────────────────────────────

VALID_MODULE_IDS = {'fileTypes', 'codecs', 'fileTypePairs', 'namingPattern'}


@dataclass
class QCConfig:
    version: str = '1.0'
    core: CoreConfig = field(default_factory=CoreConfig)
    enabledModules: List[str] = field(default_factory=list)
    modules: ModulesConfig = field(default_factory=ModulesConfig)


# ─── Serialisation helpers ────────────────────────────────────────────────────

def _new_id() -> str:
    return str(uuid.uuid4())


def default_config() -> QCConfig:
    return QCConfig()


def config_to_dict(config: QCConfig) -> dict:
    return asdict(config)


def config_from_dict(d: dict) -> QCConfig:
    core_d = d.get('core', {})
    blocks = [
        FilenameBlock(**{k: v for k, v in b.items()})
        for b in core_d.get('filenameBlocks', [])
    ]
    core = CoreConfig(
        filenameBlocks=blocks,
        allowedResolutions=core_d.get('allowedResolutions', []),
    )

    mods_d = d.get('modules', {})

    ft_entries = [FileTypeEntry(**e) for e in mods_d.get('fileTypes', {}).get('entries', [])]
    co_entries = [CodecEntry(**e) for e in mods_d.get('codecs', {}).get('entries', [])]
    fp_entries = [FileTypePairEntry(**e) for e in mods_d.get('fileTypePairs', {}).get('entries', [])]
    np_entries = [NamingPatternEntry(**e) for e in mods_d.get('namingPattern', {}).get('entries', [])]

    modules = ModulesConfig(
        fileTypes=FileTypesConfig(entries=ft_entries),
        codecs=CodecsConfig(entries=co_entries),
        fileTypePairs=FileTypePairsConfig(entries=fp_entries),
        namingPattern=NamingPatternsConfig(entries=np_entries),
    )

    return QCConfig(
        version=d.get('version', '1.0'),
        core=core,
        enabledModules=d.get('enabledModules', []),
        modules=modules,
    )


def validate_config(d: object) -> bool:
    if not isinstance(d, dict):
        return False
    if not isinstance(d.get('version'), str):
        return False
    core = d.get('core', {})
    if not isinstance(core, dict):
        return False
    if not isinstance(core.get('filenameBlocks'), list):
        return False
    if not isinstance(core.get('allowedResolutions'), list):
        return False
    enabled = d.get('enabledModules', [])
    if not isinstance(enabled, list):
        return False
    if not all(m in VALID_MODULE_IDS for m in enabled):
        return False
    mods = d.get('modules', {})
    if not isinstance(mods, dict):
        return False
    for key in ('fileTypes', 'codecs', 'fileTypePairs', 'namingPattern'):
        mod = mods.get(key, {})
        if not isinstance(mod, dict):
            return False
        if not isinstance(mod.get('entries'), list):
            return False
    return True


def load_config(path: Path) -> QCConfig:
    with open(path, 'r', encoding='utf-8') as f:
        d = json.load(f)
    if not validate_config(d):
        raise ValueError('Invalid QC config file')
    return config_from_dict(d)


def save_config(config: QCConfig, path: Path) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config_to_dict(config), f, indent=2)
