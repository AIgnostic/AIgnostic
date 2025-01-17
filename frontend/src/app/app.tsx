// Uncomment this line to use CSS modules
// import styles from './app.module.css';
import NxWelcome from './nx-welcome';
import { Route, Routes, Link } from 'react-router-dom';
import { useState } from 'react';
import Homepage from './home';
export function App() {
  return (
    <div>
      {/* <NxWelcome title="AIgnostic" /> */}
      <Homepage />

      {/* START: routes */}
      {/* These routes and navigation have been generated for you */}
      {/* Feel free to move and update them to fit your needs */}
      <br />
      <hr />
      <br />
      <div role="navigation">
        <ul>
          <li>
            <Link to="/">Home</Link>
          </li>
          <li>
            <Link to="/page-2">Page 2</Link>
          </li>
        </ul>
      </div>
      <Routes>
        <Route
          path="/"
          element={<Home />}
        />
        <Route
          path="/page-2"
          element={
            <div>
              <Link to="/">Click here to go back to root page.</Link>
            </div>
          }
        />
      </Routes>
      {/* END: routes */}
    </div>
  );
}

function Home() {
  const [text1, setText1] = useState('');
  const [text2, setText2] = useState('');

  const handleSubmit = () => {
    if (text1 && text2) {
      console.log('Textbox 1:', text1);
      console.log('Textbox 2:', text2);
    } else {
      alert('Please fill in both textboxes before submitting.');
    }
  };

  return (
    <div>
      <h1>Enter Text</h1>
      <input
        type="text"
        placeholder="Enter text 1"
        value={text1}
        onChange={(e) => setText1(e.target.value)}
      />
      <br />
      <input
        type="text"
        placeholder="Enter text 2"
        value={text2}
        onChange={(e) => setText2(e.target.value)}
      />
      <br />
      <button onClick={handleSubmit}>Submit</button>
    </div>
  );
}


export default App;
