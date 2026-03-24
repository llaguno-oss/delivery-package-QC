import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from '@dnd-kit/core';
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  arrayMove,
} from '@dnd-kit/sortable';
import { Plus, LayoutTemplate } from 'lucide-react';
import { useConfigStore } from '../../store/configStore';
import { FileNameBlockEditor } from './FileNameBlockEditor';
import type { FilenameBlock } from '../../types/config';

const TYPE_COLORS: Record<string, string> = {
  fixed: 'bg-[var(--color-gray-dim)] text-[var(--color-text-muted)] border-[var(--color-border)]',
  list: 'bg-[var(--color-blue-dim)] text-[var(--color-blue)] border-[var(--color-blue)]/30',
  wildcard: 'bg-[var(--color-yellow-dim)] text-[var(--color-yellow)] border-[var(--color-yellow)]/30',
  token: 'bg-[var(--color-green-dim)] text-[var(--color-green)] border-[var(--color-green)]/30',
};

function blockPreviewText(block: FilenameBlock): string {
  switch (block.type) {
    case 'fixed':
      return block.value || block.label;
    case 'list':
      return block.values?.length ? block.values.join('|') : block.label;
    case 'wildcard':
      return '*';
    case 'token':
      return `{${block.label}}`;
    default:
      return block.label;
  }
}

function FilenamePreview({ blocks }: { blocks: FilenameBlock[] }) {
  if (blocks.length === 0) {
    return (
      <div className="px-4 py-3 rounded-lg border border-dashed border-[var(--color-border)] bg-[var(--color-surface-1)] text-sm text-[var(--color-text-faint)] text-center">
        Add blocks below to see a filename preview
      </div>
    );
  }

  return (
    <div className="px-4 py-3 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-1)] flex flex-wrap items-center gap-0.5">
      {blocks.map((block, i) => (
        <span key={block.id} className="flex items-center gap-0.5">
          <span
            className={`inline-block px-2 py-0.5 rounded border text-xs font-mono ${TYPE_COLORS[block.type]}`}
          >
            {blockPreviewText(block)}
          </span>
          {i < blocks.length - 1 && block.separator && (
            <span className="text-[var(--color-text-faint)] text-sm font-mono">{block.separator}</span>
          )}
        </span>
      ))}
    </div>
  );
}

export function FileNameBlocks() {
  const blocks = useConfigStore((s) => s.config.core.filenameBlocks);
  const addFilenameBlock = useConfigStore((s) => s.addFilenameBlock);
  const updateFilenameBlock = useConfigStore((s) => s.updateFilenameBlock);
  const removeFilenameBlock = useConfigStore((s) => s.removeFilenameBlock);
  const reorderFilenameBlocks = useConfigStore((s) => s.reorderFilenameBlocks);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    }),
  );

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (over && active.id !== over.id) {
      const oldIndex = blocks.findIndex((b) => b.id === active.id);
      const newIndex = blocks.findIndex((b) => b.id === over.id);
      reorderFilenameBlocks(arrayMove(blocks, oldIndex, newIndex));
    }
  };

  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <LayoutTemplate size={16} className="text-[var(--color-accent)]" />
          <h2 className="text-base font-semibold text-[var(--color-text-primary)]">
            Filename Blocks
          </h2>
        </div>
        <p className="text-sm text-[var(--color-text-muted)]">
          Define the ordered components of a valid filename. Drag to reorder.
        </p>
      </div>

      {/* Live preview */}
      <FilenamePreview blocks={blocks} />

      {/* Legend */}
      <div className="flex items-center gap-3 text-xs text-[var(--color-text-muted)]">
        <span className="font-medium">Block types:</span>
        {Object.entries(TYPE_COLORS).map(([type, cls]) => (
          <span key={type} className={`px-2 py-0.5 rounded border font-mono ${cls}`}>
            {type}
          </span>
        ))}
      </div>

      {/* Column headers */}
      {blocks.length > 0 && (
        <div className="flex items-center gap-3 px-3 text-xs font-medium uppercase tracking-wider text-[var(--color-text-faint)]">
          <span className="w-4" />
          <span className="w-32">Label</span>
          <span className="w-28">Type</span>
          <span className="flex-1">Value / Options</span>
          <span className="w-20">Separator</span>
          <span className="w-8" />
        </div>
      )}

      {/* Sortable block list */}
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={blocks.map((b) => b.id)} strategy={verticalListSortingStrategy}>
          <div className="space-y-2">
            {blocks.map((block) => (
              <FileNameBlockEditor
                key={block.id}
                block={block}
                onUpdate={(patch) => updateFilenameBlock(block.id, patch)}
                onRemove={() => removeFilenameBlock(block.id)}
              />
            ))}
          </div>
        </SortableContext>
      </DndContext>

      <button onClick={addFilenameBlock} className="qc-btn-secondary w-full justify-center">
        <Plus size={14} />
        Add Block
      </button>
    </div>
  );
}
