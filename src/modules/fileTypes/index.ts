import { registerModule } from '../registry';
import { FileTypesTab } from './FileTypesTab';

registerModule({
  id: 'fileTypes',
  label: 'File Types',
  description: 'Define allowed file extensions for delivery packages.',
  icon: 'FileType',
  component: FileTypesTab,
  defaultConfig: { entries: [] },
});
