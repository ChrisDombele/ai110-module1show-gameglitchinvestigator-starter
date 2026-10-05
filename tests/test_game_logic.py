import ast
from pathlib import Path

from logic_utils import get_range_for_difficulty, parse_guess, check_guess, update_score


# --- get_range_for_difficulty ---

def test_range_easy():
    assert get_range_for_difficulty("Easy") == (1, 20)

def test_range_normal():
    assert get_range_for_difficulty("Normal") == (1, 50)

def test_range_hard():
    assert get_range_for_difficulty("Hard") == (1, 100)

def test_range_grows_with_difficulty():
    # Regression: Normal used to be larger than Hard
    easy = get_range_for_difficulty("Easy")[1]
    normal = get_range_for_difficulty("Normal")[1]
    hard = get_range_for_difficulty("Hard")[1]
    assert easy < normal < hard

def test_range_unknown_difficulty_falls_back():
    assert get_range_for_difficulty("Bogus") == (1, 50)


# --- parse_guess ---

def test_parse_valid_int():
    assert parse_guess("42") == (True, 42, None)

def test_parse_float_string_truncates():
    assert parse_guess("7.9") == (True, 7, None)

def test_parse_negative_number():
    assert parse_guess("-3") == (True, -3, None)

def test_parse_none():
    assert parse_guess(None) == (False, None, "Enter a guess.")

def test_parse_empty_string():
    assert parse_guess("") == (False, None, "Enter a guess.")

def test_parse_non_numeric():
    assert parse_guess("abc") == (False, None, "That is not a number.")

def test_parse_bad_float():
    assert parse_guess("1.2.3") == (False, None, "That is not a number.")


# --- check_guess ---

def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    outcome, _ = check_guess(50, 50)
    assert outcome == "Win"

def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    outcome, _ = check_guess(60, 50)
    assert outcome == "Too High"

def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    outcome, _ = check_guess(40, 50)
    assert outcome == "Too Low"

def test_too_high_hint_says_lower():
    # Regression: hint messages used to be swapped
    _, message = check_guess(60, 50)
    assert "LOWER" in message

def test_too_low_hint_says_higher():
    _, message = check_guess(40, 50)
    assert "HIGHER" in message

def test_win_message():
    _, message = check_guess(5, 5)
    assert "Correct" in message


# --- update_score ---

def test_win_on_first_attempt():
    assert update_score(0, "Win", 1) == 90

def test_win_points_decrease_with_attempts():
    assert update_score(0, "Win", 3) == 70

def test_win_points_floor_at_10():
    assert update_score(0, "Win", 20) == 10

def test_win_adds_to_current_score():
    assert update_score(25, "Win", 2) == 105

def test_too_low_loses_5():
    assert update_score(20, "Too Low", 1) == 15

def test_too_high_odd_attempt_loses_5():
    assert update_score(20, "Too High", 1) == 15

def test_too_high_even_attempt_gains_5():
    assert update_score(20, "Too High", 2) == 25

def test_unknown_outcome_leaves_score_unchanged():
    assert update_score(20, "Whatever", 1) == 20


# --- Bug reproduction log regressions ---

def _load_attempt_limit_map():
    # app.py is a Streamlit script, so read the dict literal instead of importing it
    tree = ast.parse((Path(__file__).parent.parent / "app.py").read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            getattr(t, "id", None) == "attempt_limit_map" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("attempt_limit_map not found in app.py")

def test_attempts_decrease_with_difficulty():
    # Regression: Easy used to allow fewer attempts than Normal
    limits = _load_attempt_limit_map()
    assert limits["Easy"] > limits["Normal"] > limits["Hard"]

def test_numeric_comparison_not_text_comparison():
    # Regression: 9 vs 50 was compared as strings ("9" > "50") giving "Too High"
    outcome, message = check_guess(9, 50)
    assert outcome == "Too Low"
    assert "HIGHER" in message

def test_guess_77_hint_says_lower():
    # Log row: guess 77 should say go lower
    assert check_guess(77, 50) == ("Too High", "📉 Go LOWER!")

def test_guess_28_hint_says_higher():
    # Log row: guess 28 should say go higher
    assert check_guess(28, 50) == ("Too Low", "📈 Go HIGHER!")

def test_first_guess_win_scores_90_on_zero_start():
    # Regression: attempts is a count of guesses made, so the 1st guess is attempt 1
    assert update_score(0, "Win", 1) == 90

def test_too_high_scoring_follows_one_based_attempts():
    # Regression: off-by-one shifted which attempts gain/lose points
    assert update_score(0, "Too High", 1) == -5
    assert update_score(-5, "Too High", 2) == 0

def test_parse_whitespace_only_is_empty():
    # Regression: whitespace-only guess must be rejected as empty
    assert parse_guess("   ") == (False, None, "Enter a guess.")

def test_empty_guess_rejected_before_attempt_counted():
    # Regression: an empty guess used to cost an attempt and be added to history.
    # app.py is a Streamlit script, so check the empty-guess guard comes before the attempts increment.
    src = (Path(__file__).parent.parent / "app.py").read_text(encoding="utf-8")
    guard = src.index('not (raw_guess or "").strip()')
    assert guard < src.index("st.session_state.attempts += 1")

def test_parse_then_check_end_to_end():
    ok, guess, _ = parse_guess("9")
    assert ok
    assert check_guess(guess, 50)[0] == "Too Low"
