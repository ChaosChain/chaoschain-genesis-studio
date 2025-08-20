
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import ERC8004DemoPage from './pages/ERC8004DemoPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/erc8004-demo" element={<ERC8004DemoPage />} />
      </Routes>
    </Router>
  );
}

export default App;
