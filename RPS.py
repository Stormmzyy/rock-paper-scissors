COUNTER = {"R": "P", "P": "S", "S": "R"}


def player(prev_play, state={}):
    # A new match starts when prev_play is empty: reset everything
    if prev_play == "" or not state:
        state.clear()
        state["opp"] = []            # opponent's moves this match
        state["mine"] = []           # my moves this match
        state["patterns"] = {}       # 5-move patterns seen from the opponent
        state["abbey_counts"] = {a + b: 0 for a in "RPS" for b in "RPS"}
        state["abbey_last"] = "R"
        state["scores"] = [0.0, 0.0, 0.0, 0.0]
        state["suggestions"] = None
    else:
        state["opp"].append(prev_play)
        # Score how each strategy's last suggestion would have done
        if state["suggestions"]:
            for i, move in enumerate(state["suggestions"]):
                if move == COUNTER[prev_play]:
                    result = 1
                elif prev_play == COUNTER[move]:
                    result = -1
                else:
                    result = 0
                state["scores"][i] = state["scores"][i] * 0.9 + result

    opp = state["opp"]
    mine = state["mine"]

    # Strategy 1: learn the opponent's 5-move patterns
    prediction = "P"
    if len(opp) > 4:
        last_five = "".join(opp[-5:])
        state["patterns"][last_five] = state["patterns"].get(last_five, 0) + 1
        candidates = ["".join(opp[-4:]) + m for m in "RPS"]
        seen = {c: state["patterns"][c] for c in candidates if c in state["patterns"]}
        if seen:
            prediction = max(seen, key=seen.get)[-1]
    pattern_move = COUNTER[prediction]

    # Strategy 2: simulate abbey, who predicts my next move from my last move
    counts = state["abbey_counts"]
    last = state["abbey_last"]
    abbey_prediction = max([last + m for m in "RPS"], key=lambda k: counts[k])[-1]
    abbey_move = COUNTER[abbey_prediction]
    anti_abbey = COUNTER[abbey_move]

    # Strategy 3: kris plays whatever beats my last move
    kris_move = COUNTER[mine[-1]] if mine else "P"
    anti_kris = COUNTER[kris_move]

    # Strategy 4: mrugesh counters my most frequent move in my last 10
    last_ten = ([""] + mine)[-10:]
    most_frequent = max(set(last_ten), key=last_ten.count)
    if most_frequent == "":
        most_frequent = "S"
    anti_mrugesh = COUNTER[COUNTER[most_frequent]]

    # Play the strategy that has been winning most recently
    suggestions = [pattern_move, anti_abbey, anti_kris, anti_mrugesh]
    best = max(range(4), key=lambda i: state["scores"][i])
    move = suggestions[best]

    # Update records
    state["suggestions"] = suggestions
    mine.append(move)
    counts[state["abbey_last"] + move] += 1
    state["abbey_last"] = move

    return move