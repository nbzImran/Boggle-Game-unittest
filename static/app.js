class BoggleGame {
    constructor(boardID) {
        this.words = new Set() //to store all the validate words
        this.score = 0;
        this.timer = 60;
        this.highscore = 0;
        this.board = $(boardID)
        this.nplays = parseInt($('b.nplays').text()); //track number of plays
        this.bindEventListeners(); // set up event listeners
        this.startTimer(); // start the countdown
    }

    

    bindEventListeners() {
        $('#guess-form').on('submit', async (eve) => {
            eve.preventDefault(); //prevent from submission
            let word = $('#word').val().trim(); // Get the word enered by the user
            if (word) {
                await this.checkWord(word); // che the word
            }
            $('#word').val(''); // clear the input
        });


        //handle hint button
        $('#hint-button').on('click', async () =>{
            await this.getHint();
        })
    }

    
    startTimer() {
        this.timerInterval = setInterval(() => {
            this.timer--;
            this.updateTimerDisplay();
            if(this.timer <= 0) {
                clearInterval(this.timerInterval);
                this.endGame();
            }
        }, 1000);
    }


    // fetch a hint from the backend
    async getHint() {
        try {
            const resp = await axios.get('/get-hint');
            const hint = resp.data.hint;

            if (hint) {
                this.showMessage(`Hint: try the word "${hint}"`, "hint")
            }else {
                this.showMessage("NO more hints avalable", "err")
            }
        } catch (error) {
            console.error("Error fetching hint:", error)
        }
    }

    updateTimerDisplay() {
        $('.timer').text(this.timer);
    }


    endGame() {
        $(".msg").text('Timer is Up! Game Over.');
        $('#guess-form input, #guess-form button').attr('disabled',true);
        
        //Post the score the backend and update nplays
        this.postScore(this.score);

        setTimeout(() => {
            if (confirm("would you like to play agian?")) {
                this.resetGame();
            }
        }, 2000)
    }


    async postScore(score) {
        try {
            const resp = await axios.post('/post-score', {score: score});
            const newHighScore = resp.data.new_highscore;

            if (newHighScore) {
                this.showMessage("new High score!", "ok");
            }

            this.nplays += 1;
            $('b.nplays').text(this.nplays);
            $('b.highscore').text(Math.max(score, this.highscore)); // dynamically update the score
        } catch (error) {
            console.error("Error Posting score:", error)
        }
    }

    
    //check the server to validate the word 
    async checkWord(word) {
        try {
            const resp = await axios.get("/check-word", { params:{word: word} });

            //handle the respnse based on the server result
            if (resp.data.result === "not-word") {
                this.showMessage(`${word} is not a valid english word`, "err")
            } else if (resp.data.result === "not-on-board") {
                this.showMessage(`${word} is not a valid word on this board`, "err")
            } else {
                this.addWord(word);
                this.score += word.length;
                this.showScore();
                this.showMessage(`Added: ${word}`, "ok")
            }
        }catch (error) {
            console.error("Error checking word:", error);
        }
    } 

    addWord(word) {
        if (this.words.has(word)) {
            this.showMessage(`${word} has already been used!`, "err")
        } else {
            this.words.add(word); // Add the word to set
            this.showWord(word); // show the word on the page
        } 
    }


    //Display the words on the UI
    showWord(word) {
        $('#word-list').append(`<li>${word}</li>`); // adding word on the list
    }


    // update the score on the UI
    showScore() {
        $('.score').text(this.score);
    }


    showMessage(msg, cls) {
        const $msg = $(".msg");
        $msg.text(msg).removeClass().addClass(`msg ${cls}`); // update the message for new text and class

        $msg.fadeIn(1000).fadeOut(3000);
    }

    resetGame() {
        this.words.clear(); //clear all words
        this.score = 0;
        this.timer = 60;
        $('#word-list').empty(); //clea the display word list
        $('.socre').text(this.score);
        $('#guess-form input, #guess-form button').removeAttr('disabled') // re-enable inputs

        // Restart the timer
        this.startTimer();
    }
}

$(document).ready(function() {
    new BoggleGame("#board"); // create a new instance of the game
})