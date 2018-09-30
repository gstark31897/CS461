import math
import random
import copy


# calculate the score for a single room
def score(members, scores):
    values = [
        scores[members[0]][members[1]] ** 2,
        scores[members[0]][members[2]] ** 2,
        scores[members[0]][members[3]] ** 2,
        scores[members[1]][members[2]] ** 2,
        scores[members[1]][members[3]] ** 2,
        scores[members[2]][members[3]] ** 2
    ]
    return math.sqrt(sum(values) / 6.0)


def run_cycle(rooms, scores, temp):
    accepted = 0
    attempted = 0
    # run until we accept 2000 changes or attempt 20000
    while accepted < 2000 and attempted < 20000:
        # pick 2 rooms to swap
        room_1 = random.choice(range(len(rooms)))
        room_2 = room_1
        while room_1 == room_2:
            room_2 = random.choice(range(len(rooms)))
        # pick 2 people to swap
        person_1 = random.choice(range(4))
        person_2 = random.choice(range(4))
        # try the swap
        temp_room_1 = copy.copy(rooms[room_1])
        temp_room_2 = copy.copy(rooms[room_2])
        temp_room_1[person_1] = rooms[room_2][person_2]
        temp_room_2[person_2] = rooms[room_1][person_1]
        # score the new rooms
        new_room_1_score = score(temp_room_1, scores)
        new_room_2_score = score(temp_room_1, scores)
        # get the score difference
        diff = (
            (new_room_1_score + new_room_2_score) -
            (score(rooms[room_1], scores) + score(rooms[room_2], scores))
        )
        # accept the change
        if diff > -temp:
            accepted += 1
            rooms[room_1] = temp_room_2
            rooms[room_2] = temp_room_1
        # increment attempted regardless
        attempted += 1
    # calculate min, average and max
    min_score = 100
    average_score = 0
    max_score = 0
    for room in rooms:
        value = score(room, scores)
        average_score += value
        if value < min_score:
            min_score = value
        if value > max_score:
            max_score = value
    average_score /= len(rooms)
    return rooms, min_score, average_score, max_score, accepted, attempted


# run simulations until we stagnate
def run_simulation(rooms, scores):
    # initial temp
    temp = 0.95
    i = 0
    # keep swapping til we're done
    while True:
        rooms, min_score, average_score, max_score, accepted, attempted = run_cycle(rooms, scores, temp)
        print('iteration: {}, min: {}, avg: {}, max: {}, accepted: {}, attempted: {}'.format(i, min_score, average_score, max_score, accepted, attempted, temp))
        temp -= 0.10
        i += 1
        if attempted == 20000 and accepted == 0:
            print('DONE')
            return


# read in the scores
scores = {}
with open('scores.txt') as file:
    i = 0
    for line in file:
        scores[i] = [int(score) for score in line.split()]
        i += 1

# generate starting room assignments
rooms = list(list(range(i, i + 4)) for i in range(0, 200, 4))
run_simulation(rooms, scores)
