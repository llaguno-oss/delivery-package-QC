import { useState } from 'react';
import { Plus, Regex } from 'lucide-react';
import { useConfigStore } from '../../store/configStore';
import { EditableList } from '../../components/shared/EditableList';
import type { NamingPatternEntry } from '../../types/config';

function isValidRegex(pattern: string): boolean {
  try {
    new RegExp(pattern);
    return true;
  } catch {
    return false;
  }
}

function NamingPatternRow({
  entry,
  onUpdate,
  onRemove,
}: {
  entry: NamingPatternEntry;
  onUpdate: (patch: Partial<NamingPatternEntry>) => void;
  onRemove: () => void;
}) {
  const valid = !entry.pattern || isValidRegex(entry.pattern);

  return (
    <EditableList.Row onRemove={onRemove}>
      <div className="flex items-start gap-3 flex-1 min-w-0">
        <div className="w-44">
          <input
            value={entry.name}
            onChange={(e) => onUpdate({ name: e.target.value })}
            placeholder="Pattern name"
            className="qc-input w-full"
          />
        </div>
        <div className="flex-1 min-w-0">
          <input
            value={entry.pattern}
            onChange={(e) => onUpdate({ pattern: e.target.value })}
            placeholder="^[A-Z]{3,6}_\d{4}.*$"
            className={`qc-input w-full font-mono text-xs ${!valid ? 'border-[var(--color-danger)] bg-[var(--color-danger-dim)]' : ''}`}
            spellCheck={false}
          />
          {!valid && (
            <p className="text-[var(--color-danger)] text-xs mt-1">Invalid regular expression</p>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <input
            value={entry.description ?? ''}
            onChange={(e) => onUpdate({ description: e.target.value })}
            placeholder="Description (optional)"
            className="qc-input w-full"
          />
        </div>
      </div>
    </EditableList.Row>
  );
}

function AddNamingPatternForm({
  onAdd,
}: {
  onAdd: (entry: Omit<NamingPatternEntry, 'id'>) => void;
}) {
  const [name, setName] = useState('');
  const [pattern, setPattern] = useState('');
  const [description, setDescription] = useState('');

  const patternValid = !pattern || isValidRegex(pattern);

  const handleAdd = () => {
    if (!name.trim() || !pattern.trim() || !patternValid) return;
    onAdd({ name: name.trim(), pattern: pattern.trim(), description: description.trim() || undefined });
    setName('');
    setPattern('');
    setDescription('');
  };

  return (
    <div className="flex items-center gap-3">
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Pattern name"
        className="qc-input w-44"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <input
        value={pattern}
        onChange={(e) => setPattern(e.target.value)}
        placeholder="^[A-Z]{3,6}_\d{4}.*$"
        className={`qc-input flex-1 font-mono text-xs ${pattern && !patternValid ? 'border-[var(--color-danger)]' : ''}`}
        spellCheck={false}
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <input
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description (optional)"
        className="qc-input flex-1"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <button
        onClick={handleAdd}
        disabled={!name.trim() || !pattern.trim() || !patternValid}
        className="qc-btn-primary"
      >
        <Plus size={14} />
        Add
      </button>
    </div>
  );
}

export function NamingPatternTab() {
  const entries = useConfigStore((s) => s.config.modules.namingPattern.entries);
  const addNamingPattern = useConfigStore((s) => s.addNamingPattern);
  const updateNamingPattern = useConfigStore((s) => s.updateNamingPattern);
  const removeNamingPattern = useConfigStore((s) => s.removeNamingPattern);

  return (
    <EditableList
      title="Naming Patterns"
      description="Define regex patterns that package filenames must match."
      icon={<Regex size={16} />}
      items={entries}
      addForm={<AddNamingPatternForm onAdd={addNamingPattern} />}
      columnHeaders={['Name', 'Pattern (regex)', 'Description']}
      renderRow={(entry) => (
        <NamingPatternRow
          key={entry.id}
          entry={entry}
          onUpdate={(patch) => updateNamingPattern(entry.id, patch)}
          onRemove={() => removeNamingPattern(entry.id)}
        />
      )}
      emptyMessage="No naming patterns defined. Add one below."
    />
  );
}
