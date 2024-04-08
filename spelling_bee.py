from lxml import html
import requests
from random import shuffle
import json
from datetime import date
from collections import defaultdict
import pandas as pd

# answer scraper
page = requests.get('https://www.sbsolver.com/answers')
tree = html.fromstring(page.content)

letters = tree.xpath('//form[@action="https://www.sbsolver.com/process.cgi"]/input[1]/@value')[0]
center = letters[0]
edges = [x.upper() for x in letters[1:]]

answers_table = tree.xpath('//table[@class="bee-set"]/tr')
pangrams = set()
answers = {}
total = 0 

# hints
two_letter_list = defaultdict(int)
grid = defaultdict(dict)
perfect = 0
bingo = False

lengths = set()
for i,tr in enumerate(answers_table):
    if i == 0: continue
    word_length = int(tr.xpath('td[@class="bee-set-num"]/text()')[0])
    word = tr[0].xpath('a/@href')[0][-1*(word_length):]
    note = tr.xpath('td[@class="bee-note"]/text()')
    if note and "pangram" in note[0]:
        pangrams.add(word)
        if len(word) == 7:
            perfect += 1
        total += 7
    points = word_length if word_length > 4 else 1
    answers[word] = points
    total += points

    # hints
    two_letter_list[word[:2]] += 1
    if len(word) in grid[word[0].upper()]:
        grid[word[0].upper()][len(word)] += 1
    else:
        grid[word[0].upper()][len(word)] = 1 

    lengths.add(len(word))

if len(grid) == 7:
    bingo = True

def display_two_letter(new_two_letter):
    curr_letter = ""
    curr_letter_total = 0
    for k,v in new_two_letter.items():
        if not curr_letter:
            curr_letter = k[0]
        if k[0] is not curr_letter:
            print(f"Total {curr_letter_total}")
            curr_letter = k[0]
            curr_letter_total = 0
        print(f"{k.upper()} x {v}", end=", ")
        curr_letter_total += v
    print(f"Total {curr_letter_total}")

for k,v in grid.items():
    for length in lengths:
        if length not in grid[k]:
            grid[k][length] = 0
    grid[k] = dict(sorted(grid[k].items()))

def display_grid(new_grid):
    df = pd.DataFrame(new_grid).T.fillna(0)
    res = df.reset_index().rename(columns={'index': 'Letter'})
    res.loc['total'] = res.sum()
    res.loc[res.index[-1], 'Letter'] = ''
    print()
    print(res.to_markdown(index=False))
    print()

today = str(date.today())

def calculate_ranking(score, total):
    percent = score/total*100
    rank = ""
    if percent >= 0: rank = "Beginner"
    if percent >= 2: rank = "Good Start"
    if percent >= 5: rank = "Moving Up"
    if percent >= 8: rank = "Good"
    if percent >= 15: rank = "Solid"
    if percent >= 25: rank = "Nice"
    if percent >= 40: rank = "Great"
    if percent >= 50: rank = "Amazing"
    if percent >= 70: rank = "Genius"
    if percent == 100: rank = "Queen Bee"
    return rank

def display_bee(center, edges):
    print(f"""
    \t    {edges[0]}\t    {edges[1]}\n
    \t{edges[2]}\t{center}\t{edges[3]}\n
    \t    {edges[4]}\t    {edges[5]}
    """)

def dump_history():
    with open('history.json', 'r') as fd:
        history = json.load(fd)

    overwrite = False
    tail = history[-1]
    if tail and tail[0] == today:
        overwrite = True

    history_dump = [today, len(words), len(answers), score, total]
    if overwrite:
        history[-1] = history_dump
    else:
        history.append(history_dump)

    with open('history.json', 'w') as fd:
        json.dump(history, fd)

# gameplay
print("Welcome to spelling bee!")
display_bee(center, edges)
help_menu = """
Help: 
    • guess letters in lowercase
    • type 'WORDS' in all caps to see which words you've guessed
    • type 'SCORE' in all caps to see your current points and rank
    • type 'HINT' in all caps to see today's hints. These will update as you guess words
    • type 'BEE' to see the center letter and edges again
    • type 'SHUFFLE' to shuffle the letters
    • type 'SAVE' to save your progress
    • type 'RESTORE' to restore your saved progress
    • type 'EXIT' in all caps to end the game. This will also save your progress
    • type 'HELP' to see this menu again

Warning: 
    SAVE/EXIT will automatically overwrite any previously saved progress.
    Remember to RESTORE if you are coming back to the game and have unsaved progress.
    Killing the program (^C) will NOT save any progress.
"""
print(help_menu)
score = 0
words = set()
guessed = set()
    
while True:
    guess = input("Guess: ")
    if guess == "WORDS": 
        if words: 
            print(f"You've guessed {len(words)}/{len(answers)} words.")
            print(words)
        else:
            print("No words guessed.")
    elif guess == "HINT":
        print(f"# Pangrams: {len(pangrams)}")
        print(f"# Perfect: {perfect}")
        print(f"BINGO: {bingo}")
        display_grid(new_grid=grid)
        display_two_letter(new_two_letter=two_letter_list)
    elif guess == "SCORE":
        print(f"Score: {score}/{total}, Rank: {calculate_ranking(score, total)}")
    elif guess == "EXIT":
        words_to_dump = [today] + list(words)
        with open('saved.json', 'w') as fd:
            json.dump(words_to_dump, fd)
        print(f"Goodbye! Final score: {score}")
        dump_history()
        break
    elif guess == "BEE":
        display_bee(center, edges)
    elif guess == "SHUFFLE":
        shuffle(edges)
        display_bee(center, edges)
    elif guess == "SAVE":
        words_to_dump = [today] + list(words)
        with open('saved.json', 'w') as fd:
            json.dump(words_to_dump, fd)
        dump_history()
    elif guess == "RESTORE":
        with open('saved.json', 'r') as fd:
            words_list = json.load(fd)
            today_dirty = words_list.pop(0)
            if today_dirty == today:
                for word in words_list:
                    # hints
                    if word not in words:
                        two_letter_list[word[:2]] -= 1
                        grid[word[0].upper()][len(word)] -= 1
                        if two_letter_list[word[:2]] == 0:
                            del two_letter_list[word[:2]]
                        total_v = 0
                        for k,v in grid[word[0].upper()].items():
                            total_v += v
                        if total_v == 0:
                            del grid[word[0].upper()]

                        words.add(word)
                        guessed.add(word)
                        score += answers[word]
                        if word in pangrams:
                            score += 7

                print("Progress restored.")
            else:
                print("ERROR: Attempting to restore progress from different date.")
    elif guess == "HELP":
        print(help_menu)
    else:
        if guess.isupper():
            print("ERROR: Unrecognized option. Guess words in lower case, use options in uppercase.")
            continue

        guess = guess.lower()
        if guess in guessed:
            print(f"You've already guessed '{guess}'")
        elif guess in answers:
            score += answers[guess]
            words.add(guess)
            guessed.add(guess)

            # hints
            two_letter_list[guess[:2]] -= 1
            grid[guess[0].upper()][len(guess)] -= 1
            if two_letter_list[guess[:2]] == 0:
                del two_letter_list[guess[:2]]
            total_v = 0
            for k,v in grid[guess[0].upper()].items():
                total_v += v
            if total_v == 0:
                del grid[guess[0].upper()]

            is_pangram = guess in pangrams
            if is_pangram:
                if len(guess) == 7:
                    print("Perfect PANGRAM")
                else:
                    print("PANGRAM")
                score += 7
            print(f"Correct! +{answers[guess]}\nScore: {score}/{total}, Rank: {calculate_ranking(score, total)}")
            if score == total:
                print("You've completed today's Spelling Bee!")
                dump_history()
                break
        else:
            print("Not in word list :(")
            guessed.add(guess)

