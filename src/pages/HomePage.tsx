import React from 'react';
import { Link } from 'react-router-dom';

const HomePage: React.FC = () => {
  return (
    <div>
      <h1>ERC-8004 Example Frontend</h1>
      <nav>
        <ul>
          <li><Link to="/erc8004-demo">ERC-8004 Demo</Link></li>
        </ul>
      </nav>
    </div>
  );
};

export default HomePage;

