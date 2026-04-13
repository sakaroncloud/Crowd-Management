import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

console.log('main.tsx: Entry point started');

const rootElement = document.getElementById('root');
if (!rootElement) {
  console.error('main.tsx: Root element not found!');
} else {
  console.log('main.tsx: Rendering App into #root');
  createRoot(rootElement).render(
    <StrictMode>
      <App />
    </StrictMode>,
  )
}

