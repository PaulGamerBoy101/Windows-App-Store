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
        #results {
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
        }
        .card:hover {
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .card img {
            max-width: 100px;
            height: auto;
            margin-bottom: 10px;
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
        #loading {
            text-align: center;
            color: #666;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Windows Applications Store</h1>
        <div class="search-bar">
            <input type="text" id="searchInput" placeholder="Search apps...">
            <button onclick="search()">Search</button>
        </div>
        <div id="results"></div>
        <div id="loading"></div>
    </div>
    <div id="overlay" onclick="closeDetails()"></div>
    <div id="details">
        <div id="detailsContent"></div>
        <button id="closeDetails" onclick="closeDetails()">Close</button>
    </div>

    <script>
        let allResults = [];

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
                    <div class="card" onclick="showDetails('${app.name}')">
                        <img src="${app.logo}" alt="${app.name} logo">
                        <strong>${app.name}</strong><br>
                        Version: ${app.version}<br>
                        Creator: ${app.creator}
                    </div>
                `).join('') : 
                '<p>No matching apps found.</p>';
        }

        function showDetails(appName) {
            const app = allResults.find(a => a.name === appName);
            if (!app) return;
            const detailsDiv = document.getElementById('detailsContent');
            detailsDiv.innerHTML = `
                <img src="${app.logo}" alt="${app.name} logo">
                <h2>${app.name}</h2>
                <p><strong>Version:</strong> ${app.version}</p>
                <p><strong>Creator:</strong> ${app.creator}</p>
                <p><strong>Sources:</strong></p>
                <ul>
                    ${app.sources.length ? app.sources.map(source => `
                        <li>${source.source}: <a href="${source.download_link}" target="_blank">${source.download_link}</a></li>
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

def start_webview():
    api = Api()
    window = webview.create_window("Windows Applications Store", html=HTML, js_api=api, width=800, height=600)
    webview.start()

if __name__ == "__main__":
    start_webview()  # Run directly in the main thread
