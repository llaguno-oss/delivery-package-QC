import { registerModule } from '../registry';
import { FileTypePairsTab } from './FileTypePairsTab';

registerModule({
  id: 'fileTypePairs',
  label: 'File Type Pairs',
  description: 'Define required companion file pairings (e.g. .mxf requires .xml sidecar).',
  icon: 'Link',
  component: FileTypePairsTab,
  defaultConfig: { entries: [] },
});
