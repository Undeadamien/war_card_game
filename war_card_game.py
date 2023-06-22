from pathlib import Path
from random import shuffle

import pygame


class Card:
    width = 100
    height = 144
    path = Path(__file__).resolve().parent / "CuteCards - asset pack" / "CuteCards.png"
    sprite = pygame.image.load(path)

    def __init__(self, value, image) -> None:
        self.value = value
        self.image = image


class Deck:
    def __init__(self, cards, pos, image) -> None:
        self.cards = cards
        self.image = image
        self.pos = pos


class Pile:
    def __init__(self, pos) -> None:
        self.cards = []
        self.pos = pos


class Game:
    title = pygame.display.set_caption("War")
    clock = pygame.time.Clock()
    fps = 60
    size = (400, 288)

    def __init__(self) -> None:
        self.surface = pygame.display.set_mode(self.size)
        self.remaining_pause = 0
        self.round = 0

        self.running = True

        self.R_deck, self.B_deck = self.create_decks()
        self.R_pile, self.B_pile = self.create_pile()

    def create_pile(self):
        center_h = self.size[0] // 2 - Card.width // 2

        pile_red = Pile((center_h, self.size[1] // 2 - Card.height))
        pile_black = Pile((center_h, self.size[1] // 2))

        return pile_red, pile_black

    def create_decks(self):
        cards = []

        for row in range(4):
            for col in range(13):
                value = col + 1
                image = (col * Card.width, row * Card.height, Card.width, Card.height)
                cards.append(Card(value, image))

        shuffle(cards)

        deck_red = Deck(
            cards[len(cards) // 2 :],
            (0, 0),
            (14 * Card.width, 2 * Card.height, Card.width, Card.height),
        )
        deck_black = Deck(
            cards[: len(cards) // 2],
            (self.size[0] - Card.width, self.size[1] - Card.height),
            (14 * Card.width, 3 * Card.height, Card.width, Card.height),
        )

        return deck_red, deck_black

    def pause(self, seconds=None):
        if seconds:
            self.remaining_pause = seconds * self.fps

        if self.remaining_pause:
            self.remaining_pause -= 1
            return True

    def battle(self):
        try:
            # no card on pile or face down card
            if not (len(self.R_pile.cards) % 2 and len(self.B_pile.cards) % 2):
                self.R_pile.cards.append(self.R_deck.cards.pop(0))
                self.B_pile.cards.append(self.B_deck.cards.pop(0))

            # compare
            elif self.R_pile.cards[-1].value == self.B_pile.cards[-1].value:
                self.round += 1
                self.R_pile.cards.append(self.R_deck.cards.pop(0))
                self.B_pile.cards.append(self.B_deck.cards.pop(0))

            elif self.R_pile.cards[-1].value < self.B_pile.cards[-1].value:
                self.round += 1
                cards = self.R_pile.cards + self.B_pile.cards
                self.R_pile.cards, self.B_pile.cards = [], []
                shuffle(cards)
                self.B_deck.cards.extend(cards)

            elif self.R_pile.cards[-1].value > self.B_pile.cards[-1].value:
                self.round += 1
                cards = self.R_pile.cards + self.B_pile.cards
                self.R_pile.cards, self.B_pile.cards = [], []
                shuffle(cards)
                self.R_deck.cards.extend(cards)

        # happend when no card to add because deck empty
        except IndexError:
            self.B_deck.cards = self.B_deck.cards + self.B_pile.cards
            shuffle(self.B_deck.cards)
            self.B_pile.cards = []

            self.R_deck.cards = self.R_deck.cards + self.R_pile.cards
            shuffle(self.R_deck.cards)
            self.R_pile.cards = []

        self.pause(0.5)

    def render_decks(self):
        for deck in (self.R_deck, self.B_deck):
            self.surface.blit(Card.sprite, deck.pos, deck.image)

    def render_piles(self):
        for pile in (self.R_pile, self.B_pile):
            if not pile.cards:
                continue

            if len(pile.cards) % 2:
                self.surface.blit(Card.sprite, pile.pos, pile.cards[-1].image)

            else:  # every two card in the pile are rendered face down
                if pile is self.R_pile:
                    self.surface.blit(Card.sprite, pile.pos, self.R_deck.image)
                if pile is self.B_pile:
                    self.surface.blit(Card.sprite, pile.pos, self.B_deck.image)

    def render(self):
        self.surface.fill("lightpink")
        self.render_decks()
        self.render_piles()
        pygame.display.update()

    def check_victory(self):
        for deck, name in ((self.R_deck.cards, "Red"), (self.B_deck.cards, "Black")):
            if len(deck) == 52:
                print(f"The {name} player as won after {self.round} rounds")
                self.running = False

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def run(self):
        while self.running:
            self.clock.tick(self.fps)
            self.handle_events()

            if not self.pause():
                self.battle()
                self.check_victory()
                self.render()


def main():
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
