import json
import pandas as pd

def calculate_ranking(percent):
    percent *= 100
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

with open('history.json', 'r') as fd:
    history = json.load(fd)
    history.pop(0)
    cols = ["date", "words_guessed", "words_total", "score", "points_total"]
    df = pd.DataFrame(history, columns=cols)

    # entire history
    avg_percent_words_guessed = (df.words_guessed / df.words_total).mean()
    avg_percent_points_scored = (df.score / df.points_total).mean()
    print("All-Time Stats")
    print(f"On average, you guess {avg_percent_words_guessed*100:.2f}% of total words.")
    print(f"You score {avg_percent_points_scored*100:.2f}% of total points.")
    print(f"Average Ranking: {calculate_ranking(avg_percent_points_scored)}\n")

    # last five
    df = df.tail(5)
    avg_percent_words_guessed = (df.words_guessed / df.words_total).mean()
    avg_percent_points_scored = (df.score / df.points_total).mean()
    print("Last 5 Days")
    print(f"On average, you guess {avg_percent_words_guessed*100:.2f}% of total words.")
    print(f"You score {avg_percent_points_scored*100:.2f}% of total points.")
    print(f"Average Ranking: {calculate_ranking(avg_percent_points_scored)}")

