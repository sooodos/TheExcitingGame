from random import randint
from qiskit import QuantumCircuit, BasicAer, execute

cards = ["H", "H", "X", "X", "CX", "SX", "SXDG"]


def run(circuit: QuantumCircuit):
    # use local simulator
    backend = BasicAer.get_backend('qasm_simulator')
    results = execute(circuit, backend=backend, shots=1024).result()
    answer = results.get_counts()
    max_value = 0
    max_key = ""
    for key, value in answer.items():
        if value > max_value:
            max_value = value
            max_key = key
    print(answer)
    if max_key == "00":
        print("Both players stay grounded :(")
        return 0
    elif max_key == "01":
        print("Player 1 is excited!")
        return 1
    elif max_key == "10":
        print("Player 2 is excited!")
        return 2
    elif max_key == "11":
        print("Both players are excited!")
        return 3
    return


def place_gate(player, field, qubit):
    card = player.pop()
    print(f"now inserting card {card} from player {qubit}")
    if card == "H":
        field.h(qubit)
    elif card == "X":
        field.x(qubit)
    elif card == "SX":
        field.sx(qubit)
    elif card == "SXdg":
        field.sxdg(qubit)
    elif card == "CX":
        if qubit == 0:
            # print(f"It seems that player {qubit + 1} sabotaged player {qubit + 2} with a C-NOT gate!")
            field.cx(qubit, qubit + 1)
        else:
            # print(f"It seems that player {qubit+1} sabotaged player {qubit} with a C-NOT gate!")
            field.cx(qubit, qubit - 1)


def create_playing_field(player1: list, player2: list) -> QuantumCircuit:
    field = QuantumCircuit(2, 2)
    player1.reverse()
    player2.reverse()
    for i in range(5):
        place_gate(player1, field, 0)
        place_gate(player2, field, 1)
    field.measure(0, 0)
    field.measure(1, 1)
    return field


def generate_deck() -> list:
    deck = []
    for j in range(4):
        for i in range(len(cards)):
            deck.append(cards[i])
    return deck


def shuffle_deck(deck: list):
    for i in range(len(deck) * 5):
        j = randint(0, len(deck) - 1)
        k = randint(0, len(deck) - 1)
        temp = deck[j]
        deck[j] = deck[k]
        deck[k] = temp


def deal_starting_hands(player1: list, player2: list, deck: list):
    for i in range(0, 10, 2):
        player1.append(deck.pop())
        player2.append(deck.pop())


def draw_from_deck(deck: list) -> str:
    return deck.pop()


def replace(replacement_choice, card, player):
    player.remove(replacement_choice)
    player.append(card)


def draw(player: list, deck: list):
    card = draw_from_deck(deck)
    print("Card drawn from deck is:" + card)
    user_choice = "?"
    while user_choice != "y" and user_choice != "n":
        user_choice = input("Do you want this card? (y/n)")
    if user_choice == "y":
        replacement_choice = input("Choose one of your cards to remove:")
        while replacement_choice not in deck:
            replacement_choice = input("Choose one of your cards to remove:")
        replace(replacement_choice, card, player)
    else:
        deck.insert(0, card)  # put the card on the bottom of the deck


def fix_hand(player1: list) -> list:
    new_hand = []
    print("Your current hand is setup like this:")
    print(player1)
    for i in range(len(player1)):
        replacement_choice = input(f"Choose one of your cards to be on position {i} :")
        while replacement_choice not in player1:
            replacement_choice = input("Choose one of your cards to remove:")
        new_hand.insert(len(new_hand), replacement_choice)
        player1.remove(replacement_choice)
        print("Cards remaining in previous hands")
        print(player1)
        print("New hand")
        print(new_hand)
    return new_hand


class Game:
    deck = generate_deck()
    shuffle_deck(deck)
    player1 = []
    player1_wins = 0
    player2 = []
    player2_wins = 0
    rounds = 0
    print("The exciting game begins!")
    while rounds <= 0:
        print("#" * (rounds + 1), end="")
        print(f"ROUND {rounds + 1}", end="")
        print("#" * (rounds + 1))
        print()
        deal_starting_hands(player1, player2, deck)
        print("Player 1")
        print(player1)
        draw(player1, deck)
        player1 = fix_hand(player1)
        print("Player 2")
        print(player2)
        draw(player2, deck)
        player2 = fix_hand(player2)
        playing_field = create_playing_field(player1, player2)
        print(playing_field)
        round_result = run(playing_field)
        if round_result == "1":
            player1_wins = player1_wins + 1
        elif round_result == "2":
            player2_wins = player2_wins + 1
        rounds = rounds + 1
    if player1_wins > player2_wins:
        print("PLAYER ONE WAS MOST EXCITED!")
    elif player2_wins > player1_wins:
        print("PLAYER TWO WAS MOST EXCITED!")
    else:
        print("PLAYERS WERE EQUALLY EXCITED!")
