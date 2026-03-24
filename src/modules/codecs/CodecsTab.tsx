import { useState } from 'react';
import { Plus, Cpu } from 'lucide-react';
import { useConfigStore } from '../../store/configStore';
import { EditableList } from '../../components/shared/EditableList';
import { TagInput } from '../../components/shared/TagInput';
import type { CodecEntry, CodecKind } from '../../types/config';

function CodecRow({
  entry,
  onUpdate,
  onRemove,
}: {
  entry: CodecEntry;
  onUpdate: (patch: Partial<CodecEntry>) => void;
  onRemove: () => void;
}) {
  return (
    <EditableList.Row onRemove={onRemove}>
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div className="flex-1 min-w-0">
          <input
            value={entry.name}
            onChange={(e) => onUpdate({ name: e.target.value })}
            placeholder="Codec name"
            className="qc-input w-full"
          />
        </div>
        <div className="w-28">
          <select
            value={entry.kind}
            onChange={(e) => onUpdate({ kind: e.target.value as CodecKind })}
            className="qc-select w-full"
          >
            <option value="video">Video</option>
            <option value="audio">Audio</option>
          </select>
        </div>
        <div className="flex-1 min-w-0">
          <TagInput
            tags={entry.aliases ?? []}
            onChange={(aliases) => onUpdate({ aliases })}
            placeholder="Add alias…"
          />
        </div>
      </div>
    </EditableList.Row>
  );
}

function AddCodecForm({ onAdd }: { onAdd: (entry: Omit<CodecEntry, 'id'>) => void }) {
  const [name, setName] = useState('');
  const [kind, setKind] = useState<CodecKind>('video');
  const [aliases, setAliases] = useState<string[]>([]);

  const handleAdd = () => {
    if (!name.trim()) return;
    onAdd({ name: name.trim(), kind, aliases });
    setName('');
    setKind('video');
    setAliases([]);
  };

  return (
    <div className="flex items-center gap-3">
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Codec name (e.g. Apple ProRes 422)"
        className="qc-input flex-1"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <select
        value={kind}
        onChange={(e) => setKind(e.target.value as CodecKind)}
        className="qc-select w-28"
      >
        <option value="video">Video</option>
        <option value="audio">Audio</option>
      </select>
      <div className="flex-1">
        <TagInput tags={aliases} onChange={setAliases} placeholder="Add alias…" />
      </div>
      <button onClick={handleAdd} disabled={!name.trim()} className="qc-btn-primary">
        <Plus size={14} />
        Add
      </button>
    </div>
  );
}

export function CodecsTab() {
  const entries = useConfigStore((s) => s.config.modules.codecs.entries);
  const addCodec = useConfigStore((s) => s.addCodec);
  const updateCodec = useConfigStore((s) => s.updateCodec);
  const removeCodec = useConfigStore((s) => s.removeCodec);

  return (
    <EditableList
      title="Allowed Codecs"
      description="Define the audio and video codecs permitted in delivery packages."
      icon={<Cpu size={16} />}
      items={entries}
      addForm={<AddCodecForm onAdd={addCodec} />}
      columnHeaders={['Codec Name', 'Type', 'Aliases']}
      renderRow={(entry) => (
        <CodecRow
          key={entry.id}
          entry={entry}
          onUpdate={(patch) => updateCodec(entry.id, patch)}
          onRemove={() => removeCodec(entry.id)}
        />
      )}
      emptyMessage="No codecs defined. Add one below."
    />
  );
}
