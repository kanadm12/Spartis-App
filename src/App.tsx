import { HashRouter, Routes, Route } from 'react-router-dom';
import MedicalInterface from './ui/components/MedicalInterface';
import ViewerPage from './ui/components/ViewerPage';

function App() {
  return (
    <HashRouter>
      <Routes>
        {/* The root path '/' will now show the upload page */}
        <Route path="/" element={<MedicalInterface />} />
        
        {/* The '/viewer' path will show the viewer page */}
        <Route path="/viewer" element={<ViewerPage />} />
      </Routes>
    </HashRouter>
  );
}

export default App;