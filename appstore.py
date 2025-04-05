import webview
import requests
import json
import time

# Your GitHub raw JSON URL
GITHUB_JSON_URL = "https://raw.githubusercontent.com/PaulGamerBoy101/Windows-App-Store/refs/heads/main/apps-list.json"

# HTML, CSS, and JS embedded as strings
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Windows Applications Store</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f0f0f0;
        }
        .container {
            max-width: 800px;
            margin: auto;
        }
        .tabs {
            display: flex;
            gap: 0;
            margin-bottom: 20px;
        }
        .tab {
            flex: 1;
            padding: 10px;
            text-align: center;
            background-color: #ddd;
            cursor: pointer;
            border-bottom: 2px solid #ccc;
        }
        .tab.active {
            background-color: #fff;
            border-bottom: 2px solid #00ff00;
            font-weight: bold;
        }
        .tab:hover {
            background-color: #eee;
        }
        .content {
            display: none;
        }
        .content.active {
            display: block;
        }
        .search-bar {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input {
            flex: 1;
            padding: 8px;
            font-size: 16px;
        }
        button {
            padding: 8px 16px;
            font-size: 16px;
            background-color: #00ff00;
            color: black;
            border: none;
            border-radius: 10px;
            cursor: pointer;
        }
        button:disabled {
            background-color: #c2ffc2;
            cursor: not-allowed;
        }
        #results, #allApps {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
        }
        .card {
            width: 200px;
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            cursor: pointer;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .card:hover {
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .card img {
            width: 100px; /* Fixed width for consistency */
            height: auto;
            margin-bottom: 10px;
            display: block;
        }
        #details {
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            max-width: 500px;
            z-index: 1000;
        }
        #overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 999;
        }
        #details img {
            max-width: 150px;
            height: auto;
            margin-bottom: 15px;
        }
        #closeDetails {
            background-color: #dc3545;
            color: white;
            padding: 5px 10px;
            border: none;
            cursor: pointer;
            margin-top: 10px;
        }
        #loading, #allLoading {
            text-align: center;
            color: #666;
            margin-top: 20px;
        }
        /* New styles for sources list */
        #details .sources-list {
            list-style-type: none;
            padding: 0;
        }
        #details .sources-list li {
            margin: 15px 0; /* More space between sources */
            line-height: 1.5;
        }
        #details .sources-list .source-title {
            font-weight: bold; /* Bold source titles */
            color: #333; /* Darker color for contrast */
            display: block; /* Ensures it’s on its own line */
            margin-bottom: 5px; /* Space between title and link */
        }
        #details .sources-list a {
            color: #0066cc; /* Blue link color */
            text-decoration: none; /* Remove underline */
            word-wrap: break-word; /* Break long URLs */
        }
        #details .sources-list a:hover {
            text-decoration: underline; /* Underline on hover */
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Windows Applications Store</h1>
        <div class="tabs">
            <div class="tab active" onclick="switchTab('all')">All</div>
            <div class="tab" onclick="switchTab('search')">Search</div>
        </div>
        <div id="allContent" class="content active">
            <div id="allApps"></div>
            <div id="allLoading"></div>
        </div>
        <div id="searchContent" class="content">
            <div class="search-bar">
                <input type="text" id="searchInput" placeholder="Search apps...">
                <button onclick="search()">Search</button>
            </div>
            <div id="results"></div>
            <div id="loading"></div>
        </div>
    </div>
    <div id="overlay" onclick="closeDetails()"></div>
    <div id="details">
        <div id="detailsContent"></div>
        <button id="closeDetails" onclick="closeDetails()">Close</button>
    </div>

    <script>
        let allResults = [];
        let allApps = [];

        // Load all apps on page load
        window.addEventListener('pywebviewready', function() {
            document.getElementById('allLoading').innerText = 'Loading all apps... Please wait.';
            window.pywebview.api.load_all_apps()
                .then(apps => {
                    allApps = apps.sort((a, b) => a.name.localeCompare(b.name)); // Sort A-Z
                    displayAllApps();
                    document.getElementById('allLoading').innerText = '';
                })
                .catch(err => {
                    document.getElementById('allApps').innerHTML = `<p>Error: ${err}</p>`;
                    document.getElementById('allLoading').innerText = '';
                });
        });

        function switchTab(tab) {
            const tabs = document.querySelectorAll('.tab');
            const contents = document.querySelectorAll('.content');
            tabs.forEach(t => t.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            document.querySelector(`.tab[onclick="switchTab('${tab}')"]`).classList.add('active');
            document.getElementById(`${tab}Content`).classList.add('active');
        }

        function search() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) {
                alert('Please enter a search term.');
                return;
            }
            document.getElementById('loading').innerText = 'Searching... Please wait.';
            document.getElementById('results').innerHTML = '';
            document.querySelector('button').disabled = true;
            window.pywebview.api.search(query)
                .then(results => {
                    allResults = results;
                    displayResults();
                    document.getElementById('loading').innerText = '';
                    document.querySelector('button').disabled = false;
                })
                .catch(err => {
                    document.getElementById('results').innerHTML = `<p>Error: ${err}</p>`;
                    document.getElementById('loading').innerText = '';
                    document.querySelector('button').disabled = false;
                });
        }

        function displayResults() {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = allResults.length ? 
                allResults.map(app => `
                    <div class="card" onclick="showDetails('${app.name}', 'search')">
                        <img src="${app.logo}" alt="${app.name} logo">
                        <strong>${app.name}</strong><br>
                        Version: ${app.version}<br>
                        Creator: ${app.creator}
                    </div>
                `).join('') : 
                '<p>No matching apps found.</p>';
        }

        function displayAllApps() {
            const allAppsDiv = document.getElementById('allApps');
            allAppsDiv.innerHTML = allApps.length ? 
                allApps.map(app => `
                    <div class="card" onclick="showDetails('${app.name}', 'all')">
                        <img src="${app.logo}" alt="${app.name} logo">
                        <strong>${app.name}</strong><br>
                        Version: ${app.version}<br>
                        Creator: ${app.creator}
                    </div>
                `).join('') : 
                '<p>No apps available.</p>';
        }

        function showDetails(appName, source) {
            const appList = source === 'all' ? allApps : allResults;
            const app = appList.find(a => a.name === appName);
            if (!app) return;
            const detailsDiv = document.getElementById('detailsContent');
            detailsDiv.innerHTML = `
                <img src="${app.logo}" alt="${app.name} logo">
                <h2>${app.name}</h2>
                <p><strong>Version:</strong> ${app.version}</p>
                <p><strong>Creator:</strong> ${app.creator}</p>
                <p><strong>Sources:</strong></p>
                <ul class="sources-list">
                    ${app.sources.length ? app.sources.map(source => `
                        <li>
                            <span class="source-title">${source.source}</span>
                            <a href="${source.download_link}" target="_blank">${source.download_link}</a>
                        </li>
                    `).join('') : '<li>No sources available</li>'}
                </ul>
            `;
            document.getElementById('overlay').style.display = 'block';
            document.getElementById('details').style.display = 'block';
        }

        function closeDetails() {
            document.getElementById('overlay').style.display = 'none';
            document.getElementById('details').style.display = 'none';
        }
    </script>
</body>
</html>
"""

class Api:
    def search(self, query):
        try:
            response = requests.get(GITHUB_JSON_URL, timeout=10)
            response.raise_for_status()
            data = json.loads(response.text)
            all_apps = data.get("apps", [])

            # Filter apps by query
            query = query.lower()
            filtered_apps = [app for app in all_apps if query in app["name"].lower()]
            return filtered_apps
        except Exception as e:
            raise Exception(f"Failed to fetch apps: {str(e)}")

    def load_all_apps(self):
        try:
            response = requests.get(GITHUB_JSON_URL, timeout=10)
            response.raise_for_status()
            data = json.loads(response.text)
            all_apps = data.get("apps", [])
            return all_apps
        except Exception as e:
            raise Exception(f"Failed to load apps: {str(e)}")

def start_webview():
    api = Api()
    window = webview.create_window("Windows Applications Store", html=HTML, js_api=api, width=840, height=600)
    webview.start(debug=False)  # Disable debug mode

if __name__ == "__main__":
    start_webview()  # Run directly in the main thread
