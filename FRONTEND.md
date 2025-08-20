# ERC-8004 Example Frontend

This is a frontend application built with Vite, React, and TypeScript that demonstrates the ERC-8004 Trustless Agents standard.

## Features

- React + TypeScript + Vite setup
- Wallet connection using Wagmi
- ERC-8004 contract interaction examples
- Responsive UI

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

## Project Structure

- `src/`: Source code
  - `pages/`: React components for each page
    - `HomePage.tsx`: Landing page
    - `ERC8004DemoPage.tsx`: ERC-8004 demonstration page
  - `App.tsx`: Main application component with routing
  - `main.tsx`: Entry point with Wagmi configuration
  - `index.css`: Global styles

## ERC-8004 Integration

The application demonstrates how to interact with ERC-8004 contracts:

1. Connect your wallet using the "Connect Wallet" button
2. View your connected address
3. Interact with ERC-8004 contracts through the demo interface

## Technologies Used

- [Vite](https://vitejs.dev/)
- [React](https://reactjs.org/)
- [TypeScript](https://www.typescriptlang.org/)
- [Wagmi](https://wagmi.sh/)
- [ethers.js](https://docs.ethers.org/)
- [React Router](https://reactrouter.com/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

