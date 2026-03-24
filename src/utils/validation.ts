import type { QCConfig, ModuleId } from '../types/config';

const VALID_MODULE_IDS: ModuleId[] = ['fileTypes', 'codecs', 'fileTypePairs', 'namingPattern'];

export function validateConfig(raw: unknown): raw is QCConfig {
  if (!raw || typeof raw !== 'object') return false;
  const obj = raw as Record<string, unknown>;

  if (typeof obj.version !== 'string') return false;
  if (!obj.core || typeof obj.core !== 'object') return false;

  const core = obj.core as Record<string, unknown>;
  if (!Array.isArray(core.filenameBlocks)) return false;
  if (!Array.isArray(core.allowedResolutions)) return false;
  if (!core.allowedResolutions.every((r: unknown) => typeof r === 'string')) return false;

  if (!Array.isArray(obj.enabledModules)) return false;
  if (!obj.enabledModules.every((m: unknown) => VALID_MODULE_IDS.includes(m as ModuleId))) return false;

  if (!obj.modules || typeof obj.modules !== 'object') return false;
  const modules = obj.modules as Record<string, unknown>;

  for (const key of ['fileTypes', 'codecs', 'fileTypePairs', 'namingPattern']) {
    if (!modules[key] || typeof modules[key] !== 'object') return false;
    const mod = modules[key] as Record<string, unknown>;
    if (!Array.isArray(mod.entries)) return false;
  }

  return true;
}
