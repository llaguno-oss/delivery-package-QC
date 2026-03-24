import { Tab } from '@headlessui/react';
import { Settings2 } from 'lucide-react';
import { AppHeader } from '../header/AppHeader';
import { CoreConfigTab } from '../core/CoreConfigTab';
import { ModuleManagerTab } from './ModuleManagerTab';
import { getRegistry } from '../../modules/registry';
import { useConfigStore } from '../../store/configStore';
import type { ModuleId } from '../../types/config';

export function Shell() {
  const enabledModules = useConfigStore((s) => s.config.enabledModules);
  const registry = getRegistry();
  const enabledDescriptors = registry.filter((m) => enabledModules.includes(m.id as ModuleId));

  // Tab indices: 0 = Core Config, 1..N = enabled modules, N+1 = Module Manager
  const allTabs = [
    { id: '__core__', label: 'Core Config' },
    ...enabledDescriptors.map((m) => ({ id: m.id, label: m.label })),
    { id: '__modules__', label: 'Modules' },
  ];

  return (
    <div className="flex flex-col h-full min-h-screen bg-[var(--color-surface-0)]">
      <AppHeader />

      <Tab.Group>
        {/* Tab bar */}
        <Tab.List className="flex items-center gap-1 px-6 border-b border-[var(--color-border)] bg-[var(--color-surface-1)] overflow-x-auto">
          {allTabs.map((tab) => (
            <Tab
              key={tab.id}
              className={({ selected }) =>
                `relative flex items-center gap-1.5 px-4 py-3 text-sm font-medium whitespace-nowrap transition-colors outline-none
                ${
                  selected
                    ? 'text-[var(--color-accent)] after:absolute after:bottom-0 after:left-0 after:right-0 after:h-0.5 after:bg-[var(--color-accent)] after:rounded-t'
                    : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)]'
                }
                ${tab.id === '__modules__' ? 'ml-auto' : ''}`
              }
            >
              {tab.id === '__modules__' && <Settings2 size={14} />}
              {tab.label}
            </Tab>
          ))}
        </Tab.List>

        {/* Tab panels */}
        <Tab.Panels className="flex-1 overflow-y-auto">
          {/* Core Config */}
          <Tab.Panel className="p-6 max-w-5xl mx-auto w-full">
            <CoreConfigTab />
          </Tab.Panel>

          {/* Enabled module tabs */}
          {enabledDescriptors.map((descriptor) => {
            const Component = descriptor.component;
            return (
              <Tab.Panel key={descriptor.id} className="p-6 max-w-5xl mx-auto w-full">
                <Component />
              </Tab.Panel>
            );
          })}

          {/* Module manager */}
          <Tab.Panel className="p-6 max-w-5xl mx-auto w-full">
            <ModuleManagerTab />
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}
