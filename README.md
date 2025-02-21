<div align="center">
  <h1>📊 Investment Portfolio Tracker</h1>
  <p>A Python-based tracker that fetches real-time data from Binance, Yahoo Finance, and AMFI to monitor Crypto, ETFs, and Mutual Funds, updating a Google Sheet.</p>
</div>

---

<div align="center">
  <h2>🚀 Features</h2>
</div>
<ul>
  <li>🔹 Fetches real-time <strong>crypto holdings</strong> from Binance API.</li>
  <li>🔹 Retrieves <strong>ETF prices</strong> using Yahoo Finance.</li>
  <li>🔹 Gets <strong>mutual fund NAV</strong> from AMFI.</li>
  <li>🔹 Automatically updates <strong>Google Sheets</strong> with latest portfolio data.</li>
  <li>🔹 Supports weighted average price calculation for investments.</li>
</ul>

---

<div align="center">
  <h2>📂 Project Structure</h2>
</div>
<pre>
├── 📄 .env                # Stores Binance API keys (not pushed to GitHub)
├── 📄 credentials.json    # Google Sheets API credentials (not pushed to GitHub)
├── 📄 portfolio_tracker.py # Main script for fetching & updating data
├── 📄 run_python_tracker.bat # Windows batch file to run the script
</pre>

---

<div align="center">
  <h2>⚙️ Setup & Installation</h2>
</div>
<ol>
  <li>Clone this repository:
    <pre>git clone https://github.com/yourusername/investment_tracker.git</pre>
  </li>
  <li>Install dependencies:
    <pre>pip install -r requirements.txt</pre>
  </li>
  <li>Create a <code>.env</code> file and add your Binance API credentials:</li>
  <pre>
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
  </pre>
  <li>Ensure you have a valid <code>credentials.json</code> file for Google Sheets API access.</li>
  <li>Run the tracker manually:
    <pre>python portfolio_tracker.py</pre>
  </li>
</ol>

---

<div align="center">
  <h2>📌 Usage</h2>
</div>
<ul>
  <li>To run the script on Windows using the batch file, simply double-click <code>run_python_tracker.bat</code>.</li>
  <li>The script fetches updated data and updates your Google Sheet automatically.</li>
</ul>

---

<div align="center">
  <h2>🔒 Security Notes</h2>
</div>
<ul>
  <li>🚨 Do NOT push <code>.env</code> and <code>credentials.json</code> to GitHub.</li>
  <li>🚨 Add them to <code>.gitignore</code> to keep them private.</li>
</ul>

---

<div align="center">
  <h2>📞 Contact</h2>
</div>
<p>Created by <strong>Vishwaa</strong>. Feel free to reach out!</p>
