from flask import Flask, render_template, request, session, redirect, url_for, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from boggle import Boggle

app = Flask(__name__)
app.config['SECRET_KEY'] = "MySecretKey"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

boggle_game = Boggle()


def load_words():
    with open("words.txt") as file:
        return {line.strip().lower() for line in file}
    

WORDS = load_words()


@app.route('/')
#generate a new Boggle board if not in session
def index():
    
    board = boggle_game.make_board()
    session['board'] = board

    #genrate all possible words and store them for hint
    possibel_words = boggle_game.get_all_valid_words(board)
    session['possible_words'] = list(possibel_words) #store for the hint

    highscore = session.get("highscore", 0)
    nplays = session.get("nplays",0)

    return render_template('index.html', board=board,
                           highscore=highscore,
                           nplays=nplays)



@app.route('/check-word', methods=['GET'])
def check_word():
    #Retrieve word from the form
    word = request.args.get("word").lower()
    board = session["board"]
    
    #Use the check_valid_word method from the boggle class 
    result = boggle_game.check_valid_word(board, word)

    return jsonify({'result': result})

@app.route('/get-hint', methods=['GET'])
def get_hint():
    possible_words = session.get('possible_words', [])
    if possible_words:
        import random
        hint_word = random.choice(possible_words)
        return jsonify({'hint': hint_word})
    else:
        return jsonify({'hint': None})

@app.route("/post-score", methods=["POST"])
def post_score():
    #recive score and update the score and highscore

    score = request.json.get("score", 0)
    highscore = session.get("highscore", 0)
    nplays = session.get("nplays", 0)

    session['nplays'] = nplays + 1
    session['highscore'] = max(score, highscore)


    return jsonify(new_highscore=score > highscore)

if __name__ == '__main__':
    app.run(debug=True)