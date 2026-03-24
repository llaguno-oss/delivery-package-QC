import { useState } from 'react';
import { Plus, Link } from 'lucide-react';
import { useConfigStore } from '../../store/configStore';
import { EditableList } from '../../components/shared/EditableList';
import type { FileTypePairEntry } from '../../types/config';

function FileTypePairRow({
  entry,
  onUpdate,
  onRemove,
}: {
  entry: FileTypePairEntry;
  onUpdate: (patch: Partial<FileTypePairEntry>) => void;
  onRemove: () => void;
}) {
  return (
    <EditableList.Row onRemove={onRemove}>
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div className="flex-1 min-w-0">
          <input
            value={entry.label ?? ''}
            onChange={(e) => onUpdate({ label: e.target.value })}
            placeholder="Label (e.g. MXF + XML sidecar)"
            className="qc-input w-full"
          />
        </div>
        <div className="w-28">
          <input
            value={entry.primaryExtension}
            onChange={(e) => onUpdate({ primaryExtension: e.target.value })}
            placeholder=".mxf"
            className="qc-input w-full font-mono"
          />
        </div>
        <div className="flex items-center justify-center text-[var(--color-text-muted)]">
          <span className="text-xs">requires</span>
        </div>
        <div className="w-28">
          <input
            value={entry.companionExtension}
            onChange={(e) => onUpdate({ companionExtension: e.target.value })}
            placeholder=".xml"
            className="qc-input w-full font-mono"
          />
        </div>
      </div>
    </EditableList.Row>
  );
}

function AddFileTypePairForm({
  onAdd,
}: {
  onAdd: (entry: Omit<FileTypePairEntry, 'id'>) => void;
}) {
  const [label, setLabel] = useState('');
  const [primary, setPrimary] = useState('');
  const [companion, setCompanion] = useState('');

  const handleAdd = () => {
    if (!primary.trim() || !companion.trim()) return;
    onAdd({
      label: label.trim() || undefined,
      primaryExtension: primary.trim(),
      companionExtension: companion.trim(),
    });
    setLabel('');
    setPrimary('');
    setCompanion('');
  };

  return (
    <div className="flex items-center gap-3">
      <input
        value={label}
        onChange={(e) => setLabel(e.target.value)}
        placeholder="Label (optional)"
        className="qc-input flex-1"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <input
        value={primary}
        onChange={(e) => setPrimary(e.target.value)}
        placeholder=".mxf"
        className="qc-input w-28 font-mono"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <span className="text-xs text-[var(--color-text-muted)]">requires</span>
      <input
        value={companion}
        onChange={(e) => setCompanion(e.target.value)}
        placeholder=".xml"
        className="qc-input w-28 font-mono"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <button
        onClick={handleAdd}
        disabled={!primary.trim() || !companion.trim()}
        className="qc-btn-primary"
      >
        <Plus size={14} />
        Add
      </button>
    </div>
  );
}

export function FileTypePairsTab() {
  const entries = useConfigStore((s) => s.config.modules.fileTypePairs.entries);
  const addFileTypePair = useConfigStore((s) => s.addFileTypePair);
  const updateFileTypePair = useConfigStore((s) => s.updateFileTypePair);
  const removeFileTypePair = useConfigStore((s) => s.removeFileTypePair);

  return (
    <EditableList
      title="File Type Pairs"
      description="Define required file pairings — if the primary file exists, the companion must also be present."
      icon={<Link size={16} />}
      items={entries}
      addForm={<AddFileTypePairForm onAdd={addFileTypePair} />}
      columnHeaders={['Label', 'Primary', '', 'Companion']}
      renderRow={(entry) => (
        <FileTypePairRow
          key={entry.id}
          entry={entry}
          onUpdate={(patch) => updateFileTypePair(entry.id, patch)}
          onRemove={() => removeFileTypePair(entry.id)}
        />
      )}
      emptyMessage="No file type pairs defined. Add one below."
    />
  );
}
