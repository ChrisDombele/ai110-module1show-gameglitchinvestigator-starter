def get_range_for_difficulty(difficulty: str):
    """Return (low, high) inclusive range for a given difficulty."""
    if difficulty == "Easy":
        return 1, 20
    if difficulty == "Normal":
        return 1, 50  # FIX: Normal range was 1-100, larger than Hard; ranges must grow Easy < Normal < Hard using manual mode
    if difficulty == "Hard":
        return 1, 100  # FIX: Hard range was 1-50, making it easier than Normal using manual mode
    return 1, 50


def parse_guess(raw: str):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    """
    if raw is None:
        return False, None, "Enter a guess."

    if raw.strip() == "":  # FIX: whitespace-only input counts as empty too using manual mode
        return False, None, "Enter a guess."

    try:
        if "." in raw:
            value = int(float(raw))
        else:
            value = int(raw)
    except Exception:
        return False, None, "That is not a number."

    return True, value, None


def check_guess(guess, secret):
    """
    Compare guess to secret and return (outcome, message).

    outcome examples: "Win", "Too High", "Too Low"
    """
    if guess == secret:
        return "Win", "🎉 Correct!"

    try:
        if guess > secret:
            return "Too High", "📉 Go LOWER!"  # FIX: message was swapped; a too-high guess should say go lower using manual mode
        else:
            return "Too Low", "📈 Go HIGHER!"  # FIX: message was swapped; a too-low guess should say go higher using manual mode
    except TypeError:
        g = str(guess)
        if g == secret:
            return "Win", "🎉 Correct!"
        if g > secret:
            return "Too High", "📉 Go LOWER!"  # FIX: message was swapped; a too-high guess should say go lower using manual mode
        return "Too Low", "📈 Go HIGHER!"  # FIX: message was swapped; a too-low guess should say go higher using manual mode


def update_score(current_score: int, outcome: str, attempt_number: int):
    """Update score based on outcome and attempt number."""
    if outcome == "Win":
        points = 100 - 10 * attempt_number  # FIX: removed extra +1; attempt_number is already the 1-based count of guesses made using manual mode
        if points < 10:
            points = 10
        return current_score + points

    if outcome == "Too High":
        if attempt_number % 2 == 0:
            return current_score + 5
        return current_score - 5

    if outcome == "Too Low":
        return current_score - 5

    return current_score
