import { Switch } from '@headlessui/react';
import { FileType, Cpu, Link, Regex } from 'lucide-react';
import type { ModuleDescriptor } from '../../modules/registry';

const ICON_MAP: Record<string, React.ComponentType<{ size: number }>> = {
  FileType,
  Cpu,
  Link,
  Regex,
};

interface ModuleEnableToggleProps {
  descriptor: ModuleDescriptor;
  enabled: boolean;
  onToggle: (enabled: boolean) => void;
}

export function ModuleEnableToggle({ descriptor, enabled, onToggle }: ModuleEnableToggleProps) {
  const Icon = ICON_MAP[descriptor.icon] ?? FileType;

  return (
    <div
      className={`flex flex-col gap-3 p-4 rounded-xl border transition-all ${
        enabled
          ? 'border-[var(--color-accent)] bg-[var(--color-accent-dim)]'
          : 'border-[var(--color-border)] bg-[var(--color-surface-2)] hover:border-[var(--color-border)]'
      }`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div
            className={`p-2 rounded-lg ${
              enabled
                ? 'bg-[var(--color-accent)] text-white'
                : 'bg-[var(--color-surface-3)] text-[var(--color-text-muted)]'
            }`}
          >
            <Icon size={16} />
          </div>
          <div>
            <p className="font-semibold text-sm text-[var(--color-text-primary)]">
              {descriptor.label}
            </p>
            <p className="text-xs text-[var(--color-text-muted)] mt-0.5">{descriptor.description}</p>
          </div>
        </div>
        <Switch
          checked={enabled}
          onChange={onToggle}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-accent)] ${
            enabled ? 'bg-[var(--color-accent)]' : 'bg-[var(--color-surface-3)]'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${
              enabled ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </Switch>
      </div>
    </div>
  );
}
