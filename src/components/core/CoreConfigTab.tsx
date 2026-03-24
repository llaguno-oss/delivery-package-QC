import { FileNameBlocks } from './FileNameBlocks';
import { ResolutionList } from './ResolutionList';

export function CoreConfigTab() {
  return (
    <div className="space-y-10">
      <FileNameBlocks />
      <div className="border-t border-[var(--color-border)]" />
      <ResolutionList />
    </div>
  );
}
