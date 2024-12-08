'''
    books_webapp.py
    Jeff Ondich, 25 April 2016
    Updated 4 November 2020

    A tiny Flask application that provides a website with an accompanying
    API (which is also tiny) to support that website.

    Your website and API will be more complex.
'''
import sys
import flask
import nba_api

########### Initializing Flask ###########
# Note that this stuff has to be up here at the top, because otherwise
# the @app.route lines would raise a "name not defined" exception.
app = flask.Flask(__name__, static_folder='static', template_folder='templates')
app.register_blueprint(nba_api.api, url_prefix='/api')


########### The website routes ###########
# (As you can see, there's not much of a website in this example.)
@app.route('/') 
def get_main_page():
    ''' This is the only route intended for human users '''
    return flask.render_template('index.html')


@app.route('/api/help')
def api_help():
    print('api help')
    return '''
    REQUEST: /players/search?q={search texts}?sort={sort parameter}</br>
    RESPONSE: a JSON list of dictonaries, each of which represents one player, sorted by the sort parameter (if provided, default=team), where one of the search texts contains (a substring of) the players name. Each dictionary contains the following fields.</br>
        <li>id -- (integer) SERIAL value associated with player</br>
        <li>name -- (string) player's name, i.e. 'S. Curry'</br>
        <li>team -- (string) team player is on (3 letter code, i.e. NOP)</br>
        <li>three_attempts -- (integer) number of three pt shots attempted by player in season</br>
        <li>three_makes -- (integer) ... made by player ...</br>
        <li>layup_attempts -- (integer) number of layup shots attempted ...</br>
        <li>layup_makes -- (integer) ... </br>
        <li>layup_makes -- (integer) ... </br>
        <li>jumper_attempts -- (integer) ...</br>
        <li>jumper_makes -- (integer) ...</br>
        <li>hook_attempts -- (integer) ...</br>
        <li>hook_makes -- (integer) ...</br>
        <li>ft_attempts -- (integer) ...</br>
        <li>ft_makes -- (integer) ...</br>
        <li>blocks -- (integer) number of blocks by player</br>
        <li>fouls -- (integer) number of fouls by player</br>
        <li>fouled -- (integer) number of times player was fouled</br>
        <li>rbs -- (integer) number of rebounds by player</br>
        <li>vs -- (integer) number of violations by player</br>
        <li>tos -- (integer) number of turnovers by player</br>
        <li>tos_caused -- (integer) turnovers caused by player</br>
        <li>assists -- (integer) number of assists by player</br>
        <br>
    
    REQUEST: /players/details/{player IDs}<br>
    RESPONSE: same as /players/search/..., but instead of search or sort arguments, takes a list of player IDs and returns the associated player's dictionaries.
    REQUEST: /teams/
    RESPONSE: a JSON list of dictionaries, each which represent one team that contains the following fields</br>
        <li>abbreviation -- (string) three letter representing name of team</br>
        <li>name -- (string) full name of each team</br>
        <li>total_wins -- (integer) total number of wins each team won for the season</br>
        <li>total_losses -- (integer) total number of losses each team won for the season</br>
        <li>h_wins -- (integer) total number of home wins each team won for the season</br>
        <li>h_losses -- (integer) total number of home losses each team loss for the season</br>
        <li>a_wins -- (integer) total number of away wins each team won for the season</br>
        <li>a_losses -- (integer) total number of away losses each team loss for the season</br>
        <li>ot_wins -- (integer) total number of wins in overtime each team won for the 
        season</br>
        <li>ot_losses -- (integer) total number of losses in overtime each team won for the season</br>
        <li>points_per_game -- (integer) average number of points each team has scored through the season</br>
        <li>rebounds_per_game -- (integer) average number of rebounds each team has scored through the season</br>
        <li>assists_per_game -- (integer) average number of assists each team has scored through the season</br>
        <br>

        REQUEST: /teams/team_stat/{abbreviation}
        RESPONSE: same as /teams/ but with specified team abbreviation and returns JSON dictionary of just the specified team
    '''





########### Running the website server ###########
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {0} host port'.format(sys.argv[0]), file=sys.stderr)
        exit()

    host = sys.argv[1]
    port = int(sys.argv[2])
    app.run(host=host, port=port, debug=True)

