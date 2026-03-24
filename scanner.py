"""
Scanning engine — pure Python, no Qt dependencies.
Walks a directory tree and checks each file against the active QCConfig rules.
"""
from __future__ import annotations

import json
import re
import subprocess
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from config import QCConfig, FilenameBlock

# ─── ffprobe availability ─────────────────────────────────────────────────────

FFPROBE_AVAILABLE: bool = shutil.which('ffprobe') is not None


def _run_ffprobe(file_path: Path) -> Optional[dict]:
    """Return ffprobe JSON output for the first video/audio stream, or None on failure."""
    if not FFPROBE_AVAILABLE:
        return None
    try:
        result = subprocess.run(
            [
                'ffprobe', '-v', 'quiet',
                '-print_format', 'json',
                '-show_streams',
                str(file_path),
            ],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return None
        return json.loads(result.stdout)
    except Exception:
        return None


def _get_video_stream(ffprobe_data: dict) -> Optional[dict]:
    for s in ffprobe_data.get('streams', []):
        if s.get('codec_type') == 'video':
            return s
    return None


def _get_audio_stream(ffprobe_data: dict) -> Optional[dict]:
    for s in ffprobe_data.get('streams', []):
        if s.get('codec_type') == 'audio':
            return s
    return None


# ─── Result types ─────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    rule: str
    passed: bool
    detail: str


@dataclass
class FileResult:
    path: Path          # relative to scan root
    checks: List[CheckResult] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks) if self.checks else True

    @property
    def failed_checks(self) -> List[CheckResult]:
        return [c for c in self.checks if not c.passed]


@dataclass
class ScanReport:
    root: Path
    results: List[FileResult] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)


# ─── Filename block → regex ───────────────────────────────────────────────────

def _block_segment(block: FilenameBlock) -> str:
    """Return the regex fragment for one filename block (no separator)."""
    if block.type == 'fixed':
        return re.escape(block.value) if block.value else r'[^._\-]+'
    if block.type == 'list':
        if block.values:
            return '(?:' + '|'.join(re.escape(v) for v in block.values) + ')'
        return r'[^._\-]+'
    # token / wildcard — match any non-separator run
    return r'[^._\-]+'


def build_blocks_regex(blocks: List[FilenameBlock]) -> Optional[re.Pattern]:
    """Compile a regex that matches the full filename stem against the block template."""
    if not blocks:
        return None
    parts = []
    for i, block in enumerate(blocks):
        parts.append(_block_segment(block))
        if i < len(blocks) - 1 and block.separator:
            parts.append(re.escape(block.separator))
    pattern = '^' + ''.join(parts) + '$'
    try:
        return re.compile(pattern)
    except re.error:
        return None


# ─── Individual checkers ──────────────────────────────────────────────────────

def check_file_type(file: Path, config: QCConfig) -> Optional[CheckResult]:
    if 'fileTypes' not in config.enabledModules:
        return None
    entries = config.modules.fileTypes.entries
    if not entries:
        return None
    allowed = {e.extension.lower().lstrip('.') for e in entries}
    ext = file.suffix.lower().lstrip('.')
    if ext in allowed:
        return CheckResult('File Type', True, f'.{ext} is allowed')
    allowed_display = ', '.join(f'.{e}' for e in sorted(allowed))
    return CheckResult('File Type', False, f'.{ext} not in allowed types ({allowed_display})')


def check_companion_files(file: Path, scan_root: Path, config: QCConfig) -> List[CheckResult]:
    if 'fileTypePairs' not in config.enabledModules:
        return []
    pairs = config.modules.fileTypePairs.entries
    results = []
    ext = file.suffix.lower()
    for pair in pairs:
        primary = pair.primaryExtension.lower()
        if not primary.startswith('.'):
            primary = '.' + primary
        if ext != primary:
            continue
        companion = pair.companionExtension.lower()
        if not companion.startswith('.'):
            companion = '.' + companion
        companion_path = file.with_suffix(companion)
        label = pair.label or f'{primary} → {companion}'
        if companion_path.exists():
            results.append(CheckResult('File Pair', True, f'{label}: companion {companion} found'))
        else:
            results.append(CheckResult('File Pair', False,
                                       f'{label}: missing companion {companion_path.name}'))
    return results


def check_naming_patterns(file: Path, config: QCConfig) -> Optional[CheckResult]:
    if 'namingPattern' not in config.enabledModules:
        return None
    patterns = config.modules.namingPattern.entries
    if not patterns:
        return None
    stem = file.stem
    for entry in patterns:
        try:
            if re.fullmatch(entry.pattern, stem):
                return CheckResult('Naming Pattern', True,
                                   f'Matches pattern "{entry.name}"')
        except re.error:
            continue
    names = ', '.join(f'"{e.name}"' for e in patterns)
    return CheckResult('Naming Pattern', False,
                       f'"{stem}" does not match any pattern ({names})')


def check_blocks_pattern(file: Path, config: QCConfig,
                          blocks_regex: Optional[re.Pattern]) -> Optional[CheckResult]:
    if not config.core.filenameBlocks or blocks_regex is None:
        return None
    stem = file.stem
    if blocks_regex.match(stem):
        return CheckResult('Filename Template', True, f'"{stem}" matches block template')
    return CheckResult('Filename Template', False,
                       f'"{stem}" does not match filename block template')


def check_resolution(file: Path, config: QCConfig,
                     ffprobe_data: Optional[dict]) -> Optional[CheckResult]:
    if not config.core.allowedResolutions:
        return None
    if ffprobe_data is None:
        return None
    stream = _get_video_stream(ffprobe_data)
    if stream is None:
        return None
    w = stream.get('width')
    h = stream.get('height')
    if w is None or h is None:
        return None
    res_str = f'{w}x{h}'
    allowed = config.core.allowedResolutions
    if res_str in allowed:
        return CheckResult('Resolution', True, f'{res_str} is allowed')
    return CheckResult('Resolution', False,
                       f'{res_str} not in allowed resolutions ({", ".join(allowed)})')


def check_codec(file: Path, config: QCConfig,
                ffprobe_data: Optional[dict]) -> Optional[CheckResult]:
    if 'codecs' not in config.enabledModules:
        return None
    entries = config.modules.codecs.entries
    if not entries:
        return None
    if ffprobe_data is None:
        return None

    # Collect all codec names+aliases from config
    allowed_names: set[str] = set()
    for entry in entries:
        allowed_names.add(entry.name.lower())
        for alias in entry.aliases:
            allowed_names.add(alias.lower())

    # Check video stream first, then audio
    for kind in ('video', 'audio'):
        stream = _get_video_stream(ffprobe_data) if kind == 'video' else _get_audio_stream(ffprobe_data)
        if stream is None:
            continue
        codec_name = stream.get('codec_name', '').lower()
        codec_long = stream.get('codec_long_name', '').lower()
        if codec_name in allowed_names or codec_long in allowed_names:
            return CheckResult('Codec', True, f'{kind} codec "{codec_name}" is allowed')
        # check partial match against long name
        for name in allowed_names:
            if name in codec_long or codec_long in name:
                return CheckResult('Codec', True, f'{kind} codec "{codec_name}" matches "{name}"')
        matching_entries = [e for e in entries if e.kind == kind]
        if matching_entries:
            allowed_display = ', '.join(e.name for e in matching_entries)
            return CheckResult('Codec', False,
                               f'{kind} codec "{codec_name}" not in allowed codecs ({allowed_display})')
    return None


# ─── Main scan function ───────────────────────────────────────────────────────

# File extensions that are likely media files (worth running ffprobe on)
MEDIA_EXTENSIONS = {
    '.mxf', '.mov', '.mp4', '.m4v', '.avi', '.mkv', '.wmv', '.ts', '.mts', '.m2ts',
    '.mpg', '.mpeg', '.mp2', '.mp3', '.wav', '.aif', '.aiff', '.flac', '.aac',
    '.r3d', '.braw', '.cine', '.dng', '.dpx', '.exr',
}


def scan_path(
    root: Path,
    config: QCConfig,
    progress_callback=None,  # callable(current: int, total: int)
    cancel_check=None,        # callable() -> bool; return True to abort
) -> ScanReport:
    report = ScanReport(root=root)

    if not FFPROBE_AVAILABLE:
        needs_media = (
            bool(config.core.allowedResolutions) or
            'codecs' in config.enabledModules
        )
        if needs_media:
            report.warnings.append(
                'ffprobe not found on PATH — resolution and codec checks are skipped. '
                'Install ffmpeg to enable them.'
            )

    # Collect all files first so we can report progress
    all_files = [p for p in root.rglob('*') if p.is_file()]
    total = len(all_files)

    blocks_regex = build_blocks_regex(config.core.filenameBlocks)

    for i, file_path in enumerate(all_files):
        if cancel_check and cancel_check():
            break
        if progress_callback:
            progress_callback(i + 1, total)

        result = FileResult(path=file_path.relative_to(root))

        # Run ffprobe only for media files (saves time on text/xml sidecars)
        ffprobe_data: Optional[dict] = None
        if FFPROBE_AVAILABLE and file_path.suffix.lower() in MEDIA_EXTENSIONS:
            ffprobe_data = _run_ffprobe(file_path)

        # Run each check
        checks_to_run = [
            check_file_type(file_path, config),
            check_naming_patterns(file_path, config),
            check_blocks_pattern(file_path, config, blocks_regex),
            check_resolution(file_path, config, ffprobe_data),
            check_codec(file_path, config, ffprobe_data),
        ]
        checks_to_run += check_companion_files(file_path, root, config)

        result.checks = [c for c in checks_to_run if c is not None]
        report.results.append(result)

    return report
