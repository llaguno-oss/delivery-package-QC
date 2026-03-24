import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { persist, createJSONStorage } from 'zustand/middleware';
import { v4 as uuidv4 } from 'uuid';
import type {
  QCConfig,
  ModuleId,
  FilenameBlock,
  FileTypeEntry,
  CodecEntry,
  FileTypePairEntry,
  NamingPatternEntry,
} from '../types/config';

const DEFAULT_CONFIG: QCConfig = {
  version: '1.0',
  core: {
    filenameBlocks: [],
    allowedResolutions: [],
  },
  enabledModules: [],
  modules: {
    fileTypes: { entries: [] },
    codecs: { entries: [] },
    fileTypePairs: { entries: [] },
    namingPattern: { entries: [] },
  },
};

interface ConfigStore {
  config: QCConfig;

  // Core — filename blocks
  addFilenameBlock: () => void;
  updateFilenameBlock: (id: string, patch: Partial<FilenameBlock>) => void;
  removeFilenameBlock: (id: string) => void;
  reorderFilenameBlocks: (blocks: FilenameBlock[]) => void;

  // Core — resolutions
  addResolution: (res: string) => void;
  removeResolution: (res: string) => void;

  // Module lifecycle
  enableModule: (id: ModuleId, defaultConfig?: unknown) => void;
  disableModule: (id: ModuleId) => void;

  // File types
  addFileType: (entry: Omit<FileTypeEntry, 'id'>) => void;
  updateFileType: (id: string, patch: Partial<FileTypeEntry>) => void;
  removeFileType: (id: string) => void;

  // Codecs
  addCodec: (entry: Omit<CodecEntry, 'id'>) => void;
  updateCodec: (id: string, patch: Partial<CodecEntry>) => void;
  removeCodec: (id: string) => void;

  // File type pairs
  addFileTypePair: (entry: Omit<FileTypePairEntry, 'id'>) => void;
  updateFileTypePair: (id: string, patch: Partial<FileTypePairEntry>) => void;
  removeFileTypePair: (id: string) => void;

  // Naming patterns
  addNamingPattern: (entry: Omit<NamingPatternEntry, 'id'>) => void;
  updateNamingPattern: (id: string, patch: Partial<NamingPatternEntry>) => void;
  removeNamingPattern: (id: string) => void;

  // Import / export / reset
  importConfig: (raw: QCConfig) => void;
  exportConfig: () => QCConfig;
  resetConfig: () => void;
}

export const useConfigStore = create<ConfigStore>()(
  persist(
    immer((set, get) => ({
      config: DEFAULT_CONFIG,

      // ── Filename blocks ──────────────────────────────────────────────────
      addFilenameBlock: () =>
        set((state) => {
          state.config.core.filenameBlocks.push({
            id: uuidv4(),
            type: 'token',
            label: 'block',
            separator: '_',
          });
        }),

      updateFilenameBlock: (id, patch) =>
        set((state) => {
          const block = state.config.core.filenameBlocks.find((b) => b.id === id);
          if (block) Object.assign(block, patch);
        }),

      removeFilenameBlock: (id) =>
        set((state) => {
          state.config.core.filenameBlocks = state.config.core.filenameBlocks.filter(
            (b) => b.id !== id,
          );
        }),

      reorderFilenameBlocks: (blocks) =>
        set((state) => {
          state.config.core.filenameBlocks = blocks;
        }),

      // ── Resolutions ──────────────────────────────────────────────────────
      addResolution: (res) =>
        set((state) => {
          if (!state.config.core.allowedResolutions.includes(res)) {
            state.config.core.allowedResolutions.push(res);
          }
        }),

      removeResolution: (res) =>
        set((state) => {
          state.config.core.allowedResolutions = state.config.core.allowedResolutions.filter(
            (r) => r !== res,
          );
        }),

      // ── Module lifecycle ─────────────────────────────────────────────────
      enableModule: (id) =>
        set((state) => {
          if (!state.config.enabledModules.includes(id)) {
            state.config.enabledModules.push(id);
          }
        }),

      disableModule: (id) =>
        set((state) => {
          state.config.enabledModules = state.config.enabledModules.filter((m) => m !== id);
        }),

      // ── File types ───────────────────────────────────────────────────────
      addFileType: (entry) =>
        set((state) => {
          state.config.modules.fileTypes.entries.push({ id: uuidv4(), ...entry });
        }),

      updateFileType: (id, patch) =>
        set((state) => {
          const entry = state.config.modules.fileTypes.entries.find((e) => e.id === id);
          if (entry) Object.assign(entry, patch);
        }),

      removeFileType: (id) =>
        set((state) => {
          state.config.modules.fileTypes.entries = state.config.modules.fileTypes.entries.filter(
            (e) => e.id !== id,
          );
        }),

      // ── Codecs ───────────────────────────────────────────────────────────
      addCodec: (entry) =>
        set((state) => {
          state.config.modules.codecs.entries.push({ id: uuidv4(), ...entry });
        }),

      updateCodec: (id, patch) =>
        set((state) => {
          const entry = state.config.modules.codecs.entries.find((e) => e.id === id);
          if (entry) Object.assign(entry, patch);
        }),

      removeCodec: (id) =>
        set((state) => {
          state.config.modules.codecs.entries = state.config.modules.codecs.entries.filter(
            (e) => e.id !== id,
          );
        }),

      // ── File type pairs ───────────────────────────────────────────────────
      addFileTypePair: (entry) =>
        set((state) => {
          state.config.modules.fileTypePairs.entries.push({ id: uuidv4(), ...entry });
        }),

      updateFileTypePair: (id, patch) =>
        set((state) => {
          const entry = state.config.modules.fileTypePairs.entries.find((e) => e.id === id);
          if (entry) Object.assign(entry, patch);
        }),

      removeFileTypePair: (id) =>
        set((state) => {
          state.config.modules.fileTypePairs.entries =
            state.config.modules.fileTypePairs.entries.filter((e) => e.id !== id);
        }),

      // ── Naming patterns ───────────────────────────────────────────────────
      addNamingPattern: (entry) =>
        set((state) => {
          state.config.modules.namingPattern.entries.push({ id: uuidv4(), ...entry });
        }),

      updateNamingPattern: (id, patch) =>
        set((state) => {
          const entry = state.config.modules.namingPattern.entries.find((e) => e.id === id);
          if (entry) Object.assign(entry, patch);
        }),

      removeNamingPattern: (id) =>
        set((state) => {
          state.config.modules.namingPattern.entries =
            state.config.modules.namingPattern.entries.filter((e) => e.id !== id);
        }),

      // ── Import / export / reset ───────────────────────────────────────────
      importConfig: (raw) =>
        set((state) => {
          state.config = raw;
        }),

      exportConfig: () => get().config,

      resetConfig: () =>
        set((state) => {
          state.config = DEFAULT_CONFIG;
        }),
    })),
    {
      name: 'delivery-qc-config',
      storage: createJSONStorage(() => localStorage),
    },
  ),
);
