import { getRegistry } from '../../modules/registry';
import { useConfigStore } from '../../store/configStore';
import { ModuleEnableToggle } from '../shared/ModuleEnableToggle';
import type { ModuleId } from '../../types/config';
import { Settings2 } from 'lucide-react';

export function ModuleManagerTab() {
  const enabledModules = useConfigStore((s) => s.config.enabledModules);
  const enableModule = useConfigStore((s) => s.enableModule);
  const disableModule = useConfigStore((s) => s.disableModule);
  const registry = getRegistry();

  return (
    <div className="space-y-6">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Settings2 size={16} className="text-[var(--color-accent)]" />
          <h2 className="text-base font-semibold text-[var(--color-text-primary)]">
            Extra Parameter Modules
          </h2>
        </div>
        <p className="text-sm text-[var(--color-text-muted)]">
          Enable additional configuration tabs for scanning specific package parameters.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {registry.map((descriptor) => {
          const enabled = enabledModules.includes(descriptor.id as ModuleId);
          return (
            <ModuleEnableToggle
              key={descriptor.id}
              descriptor={descriptor}
              enabled={enabled}
              onToggle={(on) => {
                if (on) enableModule(descriptor.id as ModuleId);
                else disableModule(descriptor.id as ModuleId);
              }}
            />
          );
        })}
      </div>
    </div>
  );
}
