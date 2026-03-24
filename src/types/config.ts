// ─── Filename Block ────────────────────────────────────────────────────────

export type FilenameBlockType = 'fixed' | 'wildcard' | 'list' | 'token';

export interface FilenameBlock {
  id: string;
  type: FilenameBlockType;
  label: string;
  value?: string;        // for 'fixed' type
  values?: string[];     // for 'list' type
  separator?: string;    // separator after this block: '_' | '.' | '-' | ''
}

// ─── Core Config ──────────────────────────────────────────────────────────

export interface CoreConfig {
  filenameBlocks: FilenameBlock[];
  allowedResolutions: string[];
}

// ─── Module: File Types ───────────────────────────────────────────────────

export interface FileTypeEntry {
  id: string;
  name: string;
  extension: string;
  description?: string;
}

export interface FileTypesConfig {
  entries: FileTypeEntry[];
}

// ─── Module: Codecs ───────────────────────────────────────────────────────

export type CodecKind = 'video' | 'audio';

export interface CodecEntry {
  id: string;
  name: string;
  kind: CodecKind;
  aliases?: string[];
}

export interface CodecsConfig {
  entries: CodecEntry[];
}

// ─── Module: File Type Pairs ──────────────────────────────────────────────

export interface FileTypePairEntry {
  id: string;
  primaryExtension: string;
  companionExtension: string;
  label?: string;
}

export interface FileTypePairsConfig {
  entries: FileTypePairEntry[];
}

// ─── Module: Naming Pattern / Regex ──────────────────────────────────────

export interface NamingPatternEntry {
  id: string;
  name: string;
  pattern: string;
  description?: string;
}

export interface NamingPatternsConfig {
  entries: NamingPatternEntry[];
}

// ─── Module IDs ───────────────────────────────────────────────────────────

export type ModuleId = 'fileTypes' | 'codecs' | 'fileTypePairs' | 'namingPattern';

// ─── Root Config ──────────────────────────────────────────────────────────

export interface QCConfig {
  version: string;
  core: CoreConfig;
  enabledModules: ModuleId[];
  modules: {
    fileTypes: FileTypesConfig;
    codecs: CodecsConfig;
    fileTypePairs: FileTypePairsConfig;
    namingPattern: NamingPatternsConfig;
  };
}
