import random
import copy
from concurrent.futures import ProcessPoolExecutor, as_completed


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        rank = str(self.rank)
        if self.rank > 10:
            rank = ['J', 'Q', 'K', 'A'][self.rank - 11]
        return '{}:{}'.format(self.suit, rank)


class Hand:
    def __init__(self, cards):
        self.cards = cards

    def __repr__(self):
        return str(self.cards)

    def all_combos(self, community):
        # generate all possible combos with the commnity cards
        for i in range(len(community)):
            for j in range(len(community)):
                if j == i:
                    continue
                yield [community[i], community[j]]

    def count_ranks(self, combo):
        # make a dict of rank: count
        counts = {}
        for card in combo:
            if card.rank not in counts:
                counts[card.rank] = 0
            counts[card.rank] += 1
        return counts

    def count_suits(self, combo):
        # make a dict of suit: count
        counts = {}
        for card in combo:
            if card.suit not in counts:
                counts[card.suit] = 0
            counts[card.suit] += 1
        return counts

    def one_pair(self, combo):
        # check if we have a pair
        counts = self.count_ranks(combo)
        highest = 0
        for rank, count in counts.items():
            if count == 2 and rank > highest:
                highest = rank
        # we didn't find a pair
        if highest == 0:
            return False, []
        # order the rest of the cards for scoring
        scoring = sorted(counts.keys(), reverse=True)
        scoring.remove(highest)
        scoring = [highest, *scoring]
        return True, scoring

    def two_pair(self, combo):
        # check how many pairs we have
        counts = self.count_ranks(combo)
        pairs = []
        other = []
        for rank, count in counts.items():
            if count == 2:
                pairs.append(rank)
            else:
                other.append(rank)
        # did we find two pairs
        if len(pairs) != 2:
            return False, []
        # order for scoring
        scoring = [*sorted(pairs, reverse=True), *sorted(other, reverse=True)]
        return True, scoring

    def three_of_a_kind(self, combo):
        counts = self.count_ranks(combo)
        threes = []
        other = []
        for rank, count in counts.items():
            if count == 3:
                threes.append(rank)
            if count == 2:
                # can't be 3 of a kind
                return False, []
            if count == 1:
                other.append(rank)
        # did we find a pair
        if len(threes) == 0:
            return False, []
        # order for scoring
        scoring = [threes[0], *sorted(other, reverse=True)]
        return True, scoring

    def straight(self, combo):
        counts = self.count_ranks(combo)
        ranks = sorted(counts.keys(), reverse=True)
        last_rank = 0
        for rank in ranks:
            # make sure we only have one card
            if counts[rank] != 1:
                return False, []
            # make sure it's in order
            if last_rank != 0 and last_rank != rank + 1:
                return False, []
            last_rank = rank
        return True, ranks

    def flush(self, combo):
        # make sure we have 5 of a single suit
        counts = self.count_suits(combo)
        for suit, count in counts.items():
            if count != 5:
                return False, []
        return True, sorted([card.rank for card in combo], reverse=True)

    def full_house(self, combo):
        # check if we have 3 and 2 of something
        counts = self.count_ranks(combo)
        three = 0
        two = 0
        for rank, count in counts.items():
            if count == 3:
                three = rank
            if count == 2:
                two = rank
        # make sure we have two and three things
        if three == 0 or two == 0:
            return False, []
        return True, [three]

    def four_of_a_kind(self, combo):
        # check if we have 4 of anything
        counts = self.count_ranks(combo)
        for rank, count in counts.items():
            if count == 4:
                return True, [rank]
        return False, []

    def straight_flush(self, combo):
        # make sure everything's in the same suit
        for suit, count in self.count_suits(combo).items():
            if count != 5:
                return False, []
        # check if it's a straight
        return self.straight(combo)

    def score(self, combo):
        # find the score for our combo
        # make a list of all the scoring functions
        score_funcs = [
            self.one_pair,
            self.two_pair,
            self.three_of_a_kind,
            self.straight,
            self.flush,
            self.full_house,
            self.four_of_a_kind,
            self.straight_flush]
        i = len(score_funcs)
        # iterate over them in reverse order (to prevent extra processing if we find a really high score)
        for func in reversed(score_funcs):
            passed, scoring = func(combo)
            # check if the scoring passed
            if passed:
                # return the score and the secondary scoring
                return i, scoring
            i -= 1
        # return a zero and highest cards for secondary scoring
        return 0, sorted([card.rank for card in combo], reverse=True)

    def best(self, community):
        # find our best score with all the community cards
        highest = -1
        highest_scoring = []
        # iterate over all possible combos with the community cards
        for combo in self.all_combos(community):
            # score the combo
            value, scoring = self.score([*combo, *self.cards])
            # save it if it flat out wins
            if value > highest:
                highest = value
                highest_scoring = scoring
            # compare the secondary scorings and save it if it wins
            if value == highest and compare(scoring, highest_scoring):
                highest = value
                highest_scoring = scoring
        # return the highest scoring combo
        return highest, highest_scoring


class Deck:
    def __init__(self):
        self.cards = []
        # generate the cards
        for suit in ['H', 'D', 'C', 'S']:
            for rank in range(1, 15):
                self.cards.append(Card(suit, rank))

    def deal(self, hands, size):
        # make n hands with size cards
        for i in range(hands):
            yield Hand(self.draw(size))

    def draw(self, size):
        # draw size cards
        cards = random.sample(self.cards, size)
        (self.cards.remove(card) for card in cards)
        return cards
        

# compares two seondary scores
def compare(score1, score2):
    # iterate through all the secondary scorings and return true if 1 beats 2
    for i in range(min(len(score1), len(score2))):
        if score1[i] == score2[i]:
            continue
        return score1[i] > score2[i]


# get a generator for opponent scores
def get_scores(community, players):
    # using a coroutine to return one at a time lets us skip later processing if we're beat early
    for player in players:
        yield player.best(community)


# run a single simulation
def run_simulation(deck, community, my_score, players):
    # get all the player scores
    scores = get_scores(community, deck.deal(players - 1, 3))
    # split our score out so we can use it
    my_value, my_scoring = my_score
    # check it against everyone
    for value, scoring in scores:
        # first part is the type of combination, second part is the list of ranks for secondary scoring
        if my_value < value or (my_value == value and compare(scoring, my_scoring)):
            return False
    # return true if we beat everyone
    return True


# run a single set of simulations
def run_hand(deck, community, my_score, players, count):
    # calculate how many times we should win
    wins = 0
    for i in range(count):
        if run_simulation(copy.deepcopy(deck), community, my_score, players):
            wins += 1
    # predict if we should win
    estimate = (wins / count) > (1 / players)
    # run another simulation if we think we'll win
    if estimate:
        return True, run_simulation(deck, community, my_score, players)
    return False, False


# run all 200, 100, 10 simulations for each hand
def run_hands(players):
    # make the deck
    deck = Deck()
    # get the community cards
    community = deck.draw(5)
    # make and score our hand (prevent recalculation for performance)
    my_hand = Hand(deck.draw(2))
    my_score = my_hand.best(community)
    # run 200, 100, 10 simulations
    result_200 = run_hand(copy.deepcopy(deck), community, my_score, players, 200)
    result_100 = run_hand(copy.deepcopy(deck), community, my_score, players, 100)
    result_10 = run_hand(copy.deepcopy(deck), community, my_score, players, 10)
    # return the results
    return result_200, result_100, result_10


# make some lists for storing the results
prediction_counts = [0, 0, 0]
win_counts = [0, 0, 0]
labels = ['200', '100', '10']

# run each hand in a seperate process and collect the results here for speed
with ProcessPoolExecutor(max_workers=8) as executor:
    # submit everything to the pool
    futures = [executor.submit(run_hands, 5) for i in range(500)]
    # iterate over the results as they come in
    for execution in as_completed(futures):
        results = execution.result()
        # increment the predictions and wins appropriately
        for i in range(3):
            if results[i][0]:
                prediction_counts[i] += 1
            if results[i][1]:
                win_counts[i] += 1

# print the results
for i in range(3):
    print('{}: predicted {}% actual {}%'.format(labels[i], prediction_counts[i]/500*100, win_counts[i]/500*100))

