import type { ComponentType } from 'react';
import type { ModuleId } from '../types/config';

export interface ModuleDescriptor {
  id: ModuleId;
  label: string;
  description: string;
  icon: string; // lucide icon name, used for display
  component: ComponentType;
  defaultConfig: unknown;
}

const registry: ModuleDescriptor[] = [];

export function registerModule(descriptor: ModuleDescriptor): void {
  if (!registry.find((m) => m.id === descriptor.id)) {
    registry.push(descriptor);
  }
}

export function getRegistry(): readonly ModuleDescriptor[] {
  return registry;
}

export function getModule(id: ModuleId): ModuleDescriptor | undefined {
  return registry.find((m) => m.id === id);
}
