import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';

// Register all modules (side-effect imports)
import './modules/fileTypes/index';
import './modules/codecs/index';
import './modules/fileTypePairs/index';
import './modules/namingPattern/index';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
