import random
import streamlit as st
from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit_map = {
    "Easy": 10,  # FIX: Easy had fewer attempts than Normal; Easy should have the most using manual mode
    "Normal": 8,
    "Hard": 5,
}
attempt_limit = attempt_limit_map[difficulty]

low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")

if "secret" not in st.session_state:
    st.session_state.secret = random.randint(low, high)

if "attempts" not in st.session_state:
    st.session_state.attempts = 0  # FIX: attempts counts guesses made, so it must start at 0 (was 1, which cost the player a guess) using manual mode

if "score" not in st.session_state:
    st.session_state.score = 0

if "status" not in st.session_state:
    st.session_state.status = "playing"

if "history" not in st.session_state:
    st.session_state.history = []

if "last_hint" not in st.session_state:  # FIX: store the latest hint so it survives reruns triggered by the checkbox using manual mode
    st.session_state.last_hint = None

if "game_id" not in st.session_state:  # FIX: counter used in the text input key so New Game can reset the guess box using manual mode
    st.session_state.game_id = 0

st.subheader("Make a guess")

info_slot = st.empty()  # FIX: reserve the spot here but fill it after the submit handler so attempts/history aren't one click stale using manual mode
debug_slot = st.container()  # FIX: same placeholder trick for the debug expander using manual mode

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}_{st.session_state.game_id}"  # FIX: game_id in the key gives New Game a fresh, empty text box instead of restoring the old guess using manual mode
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    st.session_state.attempts = 0  # FIX: reset to 0 to match the initial value so attempts left is consistent across games using manual mode
    st.session_state.secret = random.randint(low, high)  # FIX: use the selected difficulty's range instead of hardcoded 1-100 using manual mode
    st.session_state.last_hint = None  # FIX: clear the old hint so it doesn't carry into the new game using manual mode
    st.session_state.status = "playing"  # FIX: status stayed "won"/"lost", so the old banner showed and st.stop() blocked the new game using manual mode
    st.session_state.score = 0  # FIX: reset score so it doesn't carry over from the previous game using manual mode
    st.session_state.history = []  # FIX: reset history so old guesses don't carry over using manual mode
    st.session_state.game_id += 1  # FIX: new key for the guess input so the old guess text is cleared using manual mode
    st.rerun()  # FIX: removed st.success("New game started.") since st.rerun() wiped it before it could be seen using manual mode

if st.session_state.status != "playing":
    if st.session_state.status == "won":
        st.success("You already won. Start a new game to play again.")
    else:
        st.error("Game over. Start a new game to try again.")
    # FIX: removed st.stop() because it halted the script before the info/debug sections below were drawn, making them vanish after a win/loss using manual mode

if submit and st.session_state.status == "playing" and not (raw_guess or "").strip():  # FIX: reject an empty guess before it counts as an attempt or lands in history using manual mode
    st.session_state.last_hint = None
    st.error("Enter a guess.")
elif submit and st.session_state.status == "playing":  # FIX: only handle guesses while playing, so Submit after game over doesn't add attempts now that st.stop() is gone using manual mode
    st.session_state.attempts += 1

    ok, guess_int, err = parse_guess(raw_guess)

    if not ok:
        st.session_state.history.append(raw_guess)
        st.session_state.last_hint = None  # FIX: invalid input has no hint, so drop the stale one using manual mode
        st.error(err)
    else:
        st.session_state.history.append(guess_int)

        secret = st.session_state.secret  # FIX: removed str() cast on even attempts; it caused int-vs-str comparisons and wrong hints using manual mode

        outcome, message = check_guess(guess_int, secret)

        st.session_state.last_hint = message  # FIX: save the hint instead of drawing it only on the submit run using manual mode

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
            st.success(
                f"You won! The secret was {st.session_state.secret}. "
                f"Final score: {st.session_state.score}"
            )
        else:
            if st.session_state.attempts >= attempt_limit:
                st.session_state.status = "lost"
                st.error(
                    f"Out of attempts! "
                    f"The secret was {st.session_state.secret}. "
                    f"Score: {st.session_state.score}"
                )

# FIX: draw info and debug after the submit handler so they show the just-updated attempts, score and history using manual mode
info_slot.info(
    f"Guess a number between {low} and {high}. "  # FIX: show the real range for the difficulty, not a hardcoded 1-100 using manual mode
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

with debug_slot:
    with st.expander("Developer Debug Info"):
        st.write("Secret:", st.session_state.secret)
        st.write("Attempts:", st.session_state.attempts)
        st.write("Score:", st.session_state.score)
        st.write("Difficulty:", difficulty)
        st.write("History:", st.session_state.history)

# FIX: render the hint outside `if submit:` so toggling the checkbox shows/hides it on every rerun using manual mode
if show_hint and st.session_state.last_hint:
    st.warning(st.session_state.last_hint)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
