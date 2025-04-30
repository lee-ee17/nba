from flask import Flask, render_template, jsonify
import json
import json
app = Flask(__name__)

# Load the JSON data
with open('nba_data.json') as f:
    nba_data = json.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    # Flatten data for easier handling in JavaScript
    formatted_data = []
    
    # Iterate directly over the teams
    for team, seasons in nba_data.items():
        for season, players in seasons.items():
            # Calculate totals for all players in the season
            total_defense = sum(
                player['defensive_rebounds'] + 
                player['steals'] + 
                player['blocks'] 
                for player in players
            )
            total_offense = sum(player['points'] for player in players)
            
            formatted_data.append({
                'team': team,
                'season': season,
                'total_defense': total_defense,
                'total_offense': total_offense,
            })
    
    return jsonify(formatted_data)

if __name__ == '__main__':
    app.run(debug=True)