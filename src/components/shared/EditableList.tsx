import { type ReactNode } from 'react';
import { Trash2 } from 'lucide-react';

interface EditableListProps<T extends { id: string }> {
  title: string;
  description?: string;
  icon?: ReactNode;
  items: T[];
  addForm: ReactNode;
  columnHeaders?: string[];
  renderRow: (item: T) => ReactNode;
  emptyMessage?: string;
}

function Row({ children, onRemove }: { children: ReactNode; onRemove: () => void }) {
  return (
    <div className="group flex items-center gap-2 px-4 py-2.5 border-b border-[var(--color-border-subtle)] last:border-0 hover:bg-[var(--color-surface-3)] transition-colors">
      {children}
      <button
        onClick={onRemove}
        className="ml-auto flex-shrink-0 p-1.5 rounded text-[var(--color-text-faint)] opacity-0 group-hover:opacity-100 hover:text-[var(--color-danger)] hover:bg-[var(--color-danger-dim)] transition-all"
        title="Remove"
      >
        <Trash2 size={14} />
      </button>
    </div>
  );
}

export function EditableList<T extends { id: string }>({
  title,
  description,
  icon,
  items,
  addForm,
  columnHeaders,
  renderRow,
  emptyMessage = 'No items yet.',
}: EditableListProps<T>) {
  return (
    <div className="space-y-4">
      <div>
        <div className="flex items-center gap-2 mb-1">
          {icon && (
            <span className="text-[var(--color-accent)]">{icon}</span>
          )}
          <h2 className="text-base font-semibold text-[var(--color-text-primary)]">{title}</h2>
        </div>
        {description && (
          <p className="text-sm text-[var(--color-text-muted)]">{description}</p>
        )}
      </div>

      <div className="rounded-lg border border-[var(--color-border)] overflow-hidden">
        {columnHeaders && columnHeaders.length > 0 && (
          <div className="flex items-center gap-3 px-4 py-2 bg-[var(--color-surface-1)] border-b border-[var(--color-border)]">
            {columnHeaders.map((h, i) => (
              <span
                key={i}
                className={`text-xs font-medium uppercase tracking-wider text-[var(--color-text-faint)] ${
                  i === 0 ? 'flex-1' : i === columnHeaders.length - 1 ? 'flex-1' : 'w-28'
                }`}
              >
                {h}
              </span>
            ))}
            <span className="w-8" />
          </div>
        )}

        {items.length === 0 ? (
          <div className="px-4 py-8 text-center text-sm text-[var(--color-text-faint)]">
            {emptyMessage}
          </div>
        ) : (
          <div>{items.map(renderRow)}</div>
        )}
      </div>

      <div className="p-4 rounded-lg border border-dashed border-[var(--color-border)] bg-[var(--color-surface-1)]">
        {addForm}
      </div>
    </div>
  );
}

EditableList.Row = Row;
