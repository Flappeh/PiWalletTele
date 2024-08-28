import { useState } from "react";
import "./App.css";
import ProductBox from "./components/ProductBox";

import Shop from "./Shop";

function App() {
  return (
    <>
      <h1>Demo Pi Wallet Checker</h1>
      <div className="card">
        <ProductBox></ProductBox>
        <Shop />
        <p>
          Edit <code>src/App.tsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  );
}

export default App;
