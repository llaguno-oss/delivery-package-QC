import { registerModule } from '../registry';
import { NamingPatternTab } from './NamingPatternTab';

registerModule({
  id: 'namingPattern',
  label: 'Naming Patterns',
  description: 'Define regex patterns that delivery package filenames must match.',
  icon: 'Regex',
  component: NamingPatternTab,
  defaultConfig: { entries: [] },
});
