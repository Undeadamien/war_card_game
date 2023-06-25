from pathlib import Path
from random import shuffle

import pygame


FPS: int = 120
INTERVAL: float = 0.5  # time between each rounds, INTERVAL >= 0
SPRITES = Path(__file__).resolve().parent / "CuteCards - asset pack" / "CuteCards.png"


class Card:
    width = 100
    height = 144
    sprite = pygame.image.load(SPRITES)

    def __init__(self, value: int, image: pygame.Rect) -> None:
        self.value = value
        self.image = image  # portion of SPRITE to display


class Pile:
    def __init__(
        self, cards: list[Card], pos: tuple[int, int], image: pygame.Rect
    ) -> None:
        self.cards = cards
        self.pos = pos
        self.image = image  # portion of SPRITE to display


class Game:
    def __init__(self, *_, size=(300, 288), interval=1, fps=60) -> None:
        self.title = pygame.display.set_caption("War")
        self.surface = pygame.display.set_mode(size)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("aria", Card.width // 3)

        self.width, self.height = size

        self.fps = fps

        self.rounds = 0
        self.remaining_pause = 0
        self.interval = interval

        self.running = True

        self.red_deck, self.black_deck = self.create_decks()
        self.red_pile, self.black_pile = self.create_pile()

    def create_pile(self):
        center_h = self.width // 2 - Card.width // 2

        pile_red = Pile(
            [],
            (center_h, self.height // 2 - Card.height),
            pygame.Rect(14 * Card.width, 2 * Card.height, Card.width, Card.height),
        )
        pile_black = Pile(
            [],
            (center_h, self.height // 2),
            pygame.Rect(14 * Card.width, 3 * Card.height, Card.width, Card.height),
        )

        return pile_red, pile_black

    def create_decks(self):
        cards = []

        for row in range(4):
            for col in range(13):
                value = col + 1
                image = (col * Card.width, row * Card.height, Card.width, Card.height)
                cards.append(Card(value, image))

        shuffle(cards)

        deck_red = Pile(
            cards[len(cards) // 2 :],
            (0, 0),
            pygame.Rect(14 * Card.width, 2 * Card.height, Card.width, Card.height),
        )
        deck_black = Pile(
            cards[: len(cards) // 2],
            (self.width - Card.width, self.height - Card.height),
            pygame.Rect(14 * Card.width, 3 * Card.height, Card.width, Card.height),
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
            if not (len(self.red_pile.cards) % 2 and len(self.black_pile.cards) % 2):
                self.red_pile.cards.append(self.red_deck.cards.pop(0))
                self.black_pile.cards.append(self.black_deck.cards.pop(0))

            # compare
            elif self.red_pile.cards[-1].value == self.black_pile.cards[-1].value:
                self.rounds += 1
                self.red_pile.cards.append(self.red_deck.cards.pop(0))
                self.black_pile.cards.append(self.black_deck.cards.pop(0))

            elif self.red_pile.cards[-1].value < self.black_pile.cards[-1].value:
                self.rounds += 1
                cards = self.red_pile.cards + self.black_pile.cards
                self.red_pile.cards, self.black_pile.cards = [], []
                shuffle(cards)
                self.black_deck.cards.extend(cards)

            elif self.red_pile.cards[-1].value > self.black_pile.cards[-1].value:
                self.rounds += 1
                cards = self.red_pile.cards + self.black_pile.cards
                self.red_pile.cards, self.black_pile.cards = [], []
                shuffle(cards)
                self.red_deck.cards.extend(cards)

        # happend when no card to add because deck are empty
        # reshuffle piles into decks
        except IndexError:
            self.black_deck.cards = self.black_deck.cards + self.black_pile.cards
            shuffle(self.black_deck.cards)
            self.black_pile.cards = []

            self.red_deck.cards = self.red_deck.cards + self.red_pile.cards
            shuffle(self.red_deck.cards)
            self.red_pile.cards = []

        self.pause(self.interval)

    def rendered_decks(self):
        for deck, offset in ((self.red_deck, +80), (self.black_deck, -80)):
            self.surface.blit(Card.sprite, deck.pos, deck.image)

            # render remaining cards in decks

            label = self.font.render(f"{len(deck.cards)}", 1, (0, 0, 0))
            width, height = label.get_rect().width, label.get_rect().height
            position = (
                deck.pos[0] + Card.width // 2 - width // 2,
                deck.pos[1] + Card.height // 2 - height // 2 + offset,
            )
            self.surface.blit(label, position)

    def rendered_piles(self):
        for pile in (self.red_pile, self.black_pile):
            if not pile.cards:
                continue
            if len(pile.cards) % 2:
                self.surface.blit(Card.sprite, pile.pos, pile.cards[-1].image)
            else:  # every two card in the pile are rendered face down
                if pile is self.red_pile:
                    self.surface.blit(Card.sprite, pile.pos, self.red_deck.image)
                if pile is self.black_pile:
                    self.surface.blit(Card.sprite, pile.pos, self.black_deck.image)

    def render(self):
        self.surface.fill("lightpink")
        self.rendered_decks()
        self.rendered_piles()
        pygame.display.update()

    def check_victory(self):
        for deck in (self.red_deck.cards, self.black_deck.cards):
            if len(deck) == 52:
                self.running = False

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def run(self) -> int:
        """Return the number of round."""
        while self.running:
            self.clock.tick(self.fps)
            self.handle_events()
            if self.pause():
                continue
            self.battle()
            self.render()
            self.check_victory()

        print(self.rounds)


def main():
    pygame.init()
    game = Game(interval=INTERVAL, fps=FPS)
    game.run()


if __name__ == "__main__":
    main()
