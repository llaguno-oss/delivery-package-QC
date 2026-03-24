import { registerModule } from '../registry';
import { CodecsTab } from './CodecsTab';

registerModule({
  id: 'codecs',
  label: 'Codecs',
  description: 'Define allowed audio and video codecs.',
  icon: 'Cpu',
  component: CodecsTab,
  defaultConfig: { entries: [] },
});
