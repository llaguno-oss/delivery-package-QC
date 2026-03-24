import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { GripVertical, Trash2 } from 'lucide-react';
import { TagInput } from '../shared/TagInput';
import type { FilenameBlock, FilenameBlockType } from '../../types/config';

const SEPARATORS = [
  { value: '_', label: '_' },
  { value: '.', label: '.' },
  { value: '-', label: '-' },
  { value: '', label: 'none' },
];

const BLOCK_TYPES: { value: FilenameBlockType; label: string }[] = [
  { value: 'token', label: 'Token' },
  { value: 'fixed', label: 'Fixed' },
  { value: 'list', label: 'List' },
  { value: 'wildcard', label: 'Wildcard' },
];

interface FileNameBlockEditorProps {
  block: FilenameBlock;
  onUpdate: (patch: Partial<FilenameBlock>) => void;
  onRemove: () => void;
}

export function FileNameBlockEditor({ block, onUpdate, onRemove }: FileNameBlockEditorProps) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: block.id,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    zIndex: isDragging ? 10 : 'auto',
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className="group flex items-center gap-3 px-3 py-2.5 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface-2)] hover:border-[var(--color-accent)] transition-colors"
    >
      {/* Drag handle */}
      <button
        {...attributes}
        {...listeners}
        className="flex-shrink-0 cursor-grab active:cursor-grabbing text-[var(--color-text-faint)] hover:text-[var(--color-text-muted)] touch-none"
      >
        <GripVertical size={16} />
      </button>

      {/* Label */}
      <div className="w-32">
        <input
          value={block.label}
          onChange={(e) => onUpdate({ label: e.target.value })}
          placeholder="label"
          className="qc-input w-full text-sm"
        />
      </div>

      {/* Type */}
      <div className="w-28">
        <select
          value={block.type}
          onChange={(e) => onUpdate({ type: e.target.value as FilenameBlockType })}
          className="qc-select w-full text-sm"
        >
          {BLOCK_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {/* Type-specific value fields */}
      <div className="flex-1 min-w-0">
        {block.type === 'fixed' && (
          <input
            value={block.value ?? ''}
            onChange={(e) => onUpdate({ value: e.target.value })}
            placeholder="Fixed value"
            className="qc-input w-full text-sm font-mono"
          />
        )}
        {block.type === 'list' && (
          <TagInput
            tags={block.values ?? []}
            onChange={(values) => onUpdate({ values })}
            placeholder="Add allowed value…"
          />
        )}
        {block.type === 'wildcard' && (
          <span className="px-3 py-1 text-xs font-mono text-[var(--color-yellow)] bg-[var(--color-yellow-dim)] rounded border border-[var(--color-yellow)]/30">
            * (any value)
          </span>
        )}
        {block.type === 'token' && (
          <span className="px-3 py-1 text-xs font-mono text-[var(--color-green)] bg-[var(--color-green-dim)] rounded border border-[var(--color-green)]/30">
            {`{${block.label || 'token'}}`}
          </span>
        )}
      </div>

      {/* Separator */}
      <div className="w-20">
        <select
          value={block.separator ?? '_'}
          onChange={(e) => onUpdate({ separator: e.target.value })}
          className="qc-select w-full text-sm font-mono"
        >
          {SEPARATORS.map((s) => (
            <option key={s.value} value={s.value}>
              {s.label}
            </option>
          ))}
        </select>
      </div>

      {/* Remove */}
      <button
        onClick={onRemove}
        className="flex-shrink-0 p-1.5 rounded text-[var(--color-text-faint)] opacity-0 group-hover:opacity-100 hover:text-[var(--color-danger)] hover:bg-[var(--color-danger-dim)] transition-all"
        title="Remove block"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
}
