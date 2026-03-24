import { useState } from 'react';
import { Plus, FileType } from 'lucide-react';
import { useConfigStore } from '../../store/configStore';
import { EditableList } from '../../components/shared/EditableList';
import type { FileTypeEntry } from '../../types/config';

function FileTypeRow({
  entry,
  onUpdate,
  onRemove,
}: {
  entry: FileTypeEntry;
  onUpdate: (patch: Partial<FileTypeEntry>) => void;
  onRemove: () => void;
}) {
  return (
    <EditableList.Row onRemove={onRemove}>
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div className="flex-1 min-w-0">
          <input
            value={entry.name}
            onChange={(e) => onUpdate({ name: e.target.value })}
            placeholder="Name (e.g. MXF Container)"
            className="qc-input w-full"
          />
        </div>
        <div className="w-28">
          <input
            value={entry.extension}
            onChange={(e) => onUpdate({ extension: e.target.value })}
            placeholder=".mxf"
            className="qc-input w-full font-mono"
          />
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

function AddFileTypeForm({ onAdd }: { onAdd: (entry: Omit<FileTypeEntry, 'id'>) => void }) {
  const [name, setName] = useState('');
  const [extension, setExtension] = useState('');
  const [description, setDescription] = useState('');

  const handleAdd = () => {
    if (!name.trim() || !extension.trim()) return;
    onAdd({ name: name.trim(), extension: extension.trim(), description: description.trim() || undefined });
    setName('');
    setExtension('');
    setDescription('');
  };

  return (
    <div className="flex items-center gap-3">
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name (e.g. MXF Container)"
        className="qc-input flex-1"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <input
        value={extension}
        onChange={(e) => setExtension(e.target.value)}
        placeholder=".mxf"
        className="qc-input w-28 font-mono"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <input
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description (optional)"
        className="qc-input flex-1"
        onKeyDown={(e) => e.key === 'Enter' && handleAdd()}
      />
      <button onClick={handleAdd} disabled={!name.trim() || !extension.trim()} className="qc-btn-primary">
        <Plus size={14} />
        Add
      </button>
    </div>
  );
}

export function FileTypesTab() {
  const entries = useConfigStore((s) => s.config.modules.fileTypes.entries);
  const addFileType = useConfigStore((s) => s.addFileType);
  const updateFileType = useConfigStore((s) => s.updateFileType);
  const removeFileType = useConfigStore((s) => s.removeFileType);

  return (
    <EditableList
      title="Allowed File Types"
      description="Define the file extensions that delivery packages may contain."
      icon={<FileType size={16} />}
      items={entries}
      addForm={<AddFileTypeForm onAdd={addFileType} />}
      columnHeaders={['Name', 'Extension', 'Description']}
      renderRow={(entry) => (
        <FileTypeRow
          key={entry.id}
          entry={entry}
          onUpdate={(patch) => updateFileType(entry.id, patch)}
          onRemove={() => removeFileType(entry.id)}
        />
      )}
      emptyMessage="No file types defined. Add one below."
    />
  );
}
