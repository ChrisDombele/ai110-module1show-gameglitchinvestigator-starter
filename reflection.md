# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
  - The game at first glace looked like it was working. I noticed that as each guess that I made, the prompt kept telling me to go higher. Even when I already eaither guessed or passed the secret number. I also noticed that the show hint check box was not working correctly.
- List at least two concrete bugs you noticed at the start
   1. New game resets the secret and attemps but it does not reset guess submissions and score
   2. When guessing a number higher than the secret, the hint still says to go higher
   3. The hint goes away when unchecked but does not come back
  (for example: "the hints were backwards").

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error | Suspected Code Location |
|-------|-------------------|-----------------|------------------------|------------------------|
|77|Hint: Go lower|Hint: Go higher|None|app.py, logic_utils.py|
|28|Hint: Go higher |Hint: Go lower |None|app.py, logic_utils.py|
|Toggle hint box |Hint box goes away then comes back  |Hint box goes away but does not come back |None|app.py|
|Start new game after winning or losing|All stats and numbers reset, the win/lose banner goes away, the guess box is empty and the game can be played again|Some stats and numbers reset but the "You already won" / "Game over" banner stayed and the game could no longer accept guesses. Score and history also carried over from the last game, the old guess text stayed in the guess box, and the "New game started." message never showed. Causes: the New Game block never reset `status`, so it stayed "won"/"lost" and `st.stop()` blocked the game; it also never reset `score` or `history`; the text input key (`guess_input_{difficulty}`) kept its stored value across reruns; and `st.rerun()` wiped the `st.success` message. Fix: New Game now sets `status` to "playing", resets `score` to 0 and `history` to [], and increments `st.session_state.game_id`, which is part of the guess input key so a fresh empty box is created. The `st.success` message was removed. Not yet tested in the running app|None|app.py (New Game block, `if st.session_state.status != "playing"` check, guess `st.text_input` key)|
|Difficulty change to test normal medium hard|From easy to hard, attempts would increase|Attempts from easy to hard are mixed up|None|app.py, get_range_for_difficulty|
|Guess 9 on an even-numbered attempt (secret is 50)|Hint: Go higher (9 is less than 50)|Hint says the guess is too high. The secret is converted to a string on even attempts, so the comparison is text-based ("9" > "50") instead of numeric|None. The int vs str comparison raises a TypeError that is silently caught by the try/except in check_guess|app.py (secret str() cast on even attempts), check_guess TypeError fallback|
|Submit a guess, uncheck "Show hint", then re-check it (fix for the hint checkbox bug)|The hint disappears when unchecked and the same hint comes back when re-checked|Before the fix, the hint disappeared but never returned. The hint was only drawn inside `if submit:`, which is true only on the run triggered by the Submit button. Toggling the checkbox reruns the script with `submit` False, and the hint text was a local variable that was lost between runs. Fix: the hint is now saved to `st.session_state.last_hint` and drawn after the submit block with `if show_hint and st.session_state.last_hint`. `last_hint` is also cleared on New Game and on invalid input. Not yet tested in the running app|None|app.py (hint rendered only inside `if submit:`, hint not stored in session state)|
|Compare attempts allowed across Easy, Normal and Hard in the sidebar|Attempts decrease with difficulty: Easy has the most, Hard has the fewest|Easy allowed 6, Normal 8 and Hard 5, so Easy had fewer attempts than Normal. Fix: Easy is now 10 (Normal 8 and Hard 5 unchanged) so attempts go Easy > Normal > Hard. Not yet tested in the running app|None|app.py (attempt_limit_map)|
|Compare the number ranges for Normal and Hard in the sidebar|The range grows with difficulty: Easy smallest, Hard largest|Normal was 1 to 100 and Hard was 1 to 50, so Hard was easier to guess than Normal. Fix: Normal is now 1 to 50 and Hard is 1 to 100 (Easy stays 1 to 20). Not yet tested in the running app|None|app.py, get_range_for_difficulty|
|Select Easy or Hard, then click New Game|The new secret is inside the range for the selected difficulty|The secret was always drawn from `random.randint(1, 100)`, so on Easy (1 to 20) the secret could be far outside the shown range. Fix: New Game now uses `random.randint(low, high)`. Not yet tested in the running app|None|app.py (New Game block)|
|Select Easy or Hard and read the "Guess a number between..." message|The message shows the range for the selected difficulty|The message always said "between 1 and 100" no matter the difficulty. Fix: the message now uses `{low}` and `{high}`. Not yet tested in the running app|None|app.py (st.info message)|
|Start a game and compare "Attempts left" before and after clicking New Game, then play a full game on Normal (8 attempts) and win on the first guess|Attempts left starts at the full limit (8) for every game, the player gets exactly 8 guesses, and a first-guess win scores 90|`attempts` started at 1 on the first game but New Game reset it to 0, so the counter was off by one and the two games did not match. The first attempted fix set New Game to 1 to match, which hid the mismatch but kept the real bug: "Attempts left" showed 7 on a fresh game, the loss check `attempts >= attempt_limit` ended the game after only 7 guesses, and the already-incremented count was passed to `update_score`, whose `100 - 10 * (attempt_number + 1)` formula gave a first-guess win 70 instead of 90 and shifted the odd/even "Too High" scoring by one. Fix: `attempts` now starts at 0 both on first load and in New Game (it counts guesses made), and the extra `+ 1` was removed from the win formula so it is `100 - 10 * attempt_number`. Not yet tested in the running app|None|app.py (session_state.attempts initial value, New Game block, `update_score` win formula)|
|Submit a guess for the first time and look at "Attempts left" and the Developer Debug Info (attempts, score, history)|The info box and debug section update immediately to show the guess that was just submitted|The first Submit click changed nothing on screen. The numbers only caught up after the second click, so they always lagged one submission behind. The script runs top to bottom, and the "Attempts left" box and debug expander were drawn above the `if submit:` handler, so they showed the old `attempts`, `score` and `history` before the handler updated them. Fix: reserve their spot at the original position with `info_slot = st.empty()` and `debug_slot = st.container()`, then fill them after the submit handler so the layout stays the same but they show the updated state. `st.rerun()` was not used because it would wipe the balloons and win/lose messages. Not yet tested in the running app|None|app.py (st.info and Developer Debug Info drawn before the `if submit:` block, info_slot / debug_slot)|
|Run out of attempts (or win), then click Submit Guess again|The "Game over" / "You already won" message shows, and the "Attempts left" info box and "Developer Debug Info" expander stay visible. The extra Submit does not change attempts, score or history|The "Attempts left" box and the "Developer Debug Info" expander disappeared. On the extra Submit the script reran from the top, `status` was already "lost"/"won", and `st.stop()` halted the script before the info and debug sections at the bottom were drawn. The same happened after a win. Fix: removed `st.stop()` so the script reaches the info and debug sections on every run, and changed `if submit:` to `if submit and st.session_state.status == "playing"` so Submit after game over does not add an attempt, append to history or change the score. Not yet tested in the running app|None|app.py (`st.stop()` in the `if st.session_state.status != "playing"` block, `if submit:` handler, info_slot / debug_slot rendering)|
|Leave the guess box empty (or only spaces) and click Submit Guess|An "Enter a guess." error shows, and the empty guess does not use an attempt or get added to history|The empty guess was accepted as a submission. The submit handler ran `attempts += 1` and appended the raw empty text to `history` before `parse_guess` rejected it, so the player lost an attempt (and could lose the game) for submitting nothing. A whitespace-only guess also skipped the empty check in `parse_guess` and showed "That is not a number." Fix: `app.py` now checks for an empty or whitespace-only guess first and only shows "Enter a guess." without touching attempts, score or history, and `parse_guess` treats whitespace-only input as empty using `raw.strip()`. Not yet tested in the running app|None|app.py (`if submit` handler, `attempts += 1` before validation), logic_utils.py (parse_guess)|

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
  - Then only AI tool I used on this project was Claude Code
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
  - I asked Claude to explain the logic of a glitch that I found. The glitch was that the hint suggestions were wrong for the guess that was submitted. Claude explained the glitch and found that the hint messages are swapped relative to the outcome. It suggested to swatch the messages wich I believe is the correct fix. I verified this by looking at the code to check the logic and to then test the same bug and view the results to see if it was fixed.
  - Without asking the AI also found another bug and suggested a fix. The bug was on even-numbered attempts the secret is converted to a string before it's passed to check_guess. I looked at the file and line the bug was in and confirmed the bug. The fix was to remove the str() cast and to remove the try/execpt TypeError. I did not encounter this bug while testing the game the first few times but I verfied it later and the fix removed the bug.
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.
  - There was an issue with counting attempts with starting from 1 instead of zero. The AI came up with a solution that made sense but after testing the fix, I noticed that the issue with counting still persisted. Instead of blindly accepting the first fix and moving on, I had to re-examin the fix and continue to debug with the AI. After the second attempt, testing the game verified that the second change was needed becuase the second attempt at fixing the code worked.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
  - I decided if a bug was really fixed by comparing the results from when the bug was discoverd to when the fix was implemented. If the output was different and was logical to how the game was supposed to run, then I concluded that the bug was fixed.
- Describe at least one test you ran (manual or using pytest)
  and what it showed you about your code.
  - One test I ran was test_parse_valid_int(). This test tests for a valid integer being passed. This test was done by using pytest. This showed that the code that was written accepted a positive integer and would be accepted as a valid guess.
- Did AI help you design or understand any tests? How?
  - Yes, AI helped both the designs and understanding of the tests. The fixes that the AI came up with also included its own set of tests. I felt this would check if what the AI was writing was working as I intended. The prompts that I promted contained the explanation of the bug, the fix, and the tests that would be assosciated with it.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
  - The way I would describe Streamlit "reruns" would be to say that everytime a button is clicked or there is a change that has to occur to reflect a users input, Streamlit recreates the page by running the code from top to bottom. This would happen each and everytime.
  - Session state is is a built-in dictionary-esc memory object that preserves variables and data across reruns for a browser tab. It essentaily allows for information to be saved that would normally be wiped clean on a rerun.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
    - One habbit that I would reuse in the future would be to create tests for every feature that is produced. Before AI, creating tests along side a ferature would be time consuming but with AI, the work is a lot faster.
- What is one thing you would do differently next time you work with AI on a coding task?
  - I would ask the AI to find the general area if not the exact area where a bug a a feature would be instead of wasting time and hunting it down myself. This can be time consuming depending on the size of the codebase.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
  - This project has helped me see that AI generated code is heavily dependent on the users prompts. Before this course and project, I felt as if my prompts were too vague. Taking the time to type out exaclty what I need to fix or implement creates either poorly written code or a well implemented feature.
