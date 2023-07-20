import pathlib
import random

import pygame

FPS: int = 60
SPEED: float = 0  # time between each, card must be non negative
SPRITES = pathlib.Path(__file__).parent / "asset" / "CuteCards.png"


class Card:
    w = 100
    h = 144
    sprite = pygame.image.load(SPRITES)

    def __init__(
        self,
        value: int,
        image: pygame.Rect,
    ):
        self.value = value
        self.image = image  # portion of SPRITES to display


class Pile:
    def __init__(
        self,
        cards: list[Card],
        pos: tuple[int, int],
        image: pygame.Rect,
    ):
        self.cards = cards
        self.image = image  # portion of SPRITES to display
        self.pos = pos

    def last(self):
        return self.cards[-1]

    def even(self):
        return len(self.cards) % 2 == 1


class Game:
    def __init__(
        self,
        fps: int = 60,
        size: tuple[int, int] = (3 * Card.w, 2 * Card.h),
        speed: int = 0.5,
        close: bool = False,
    ):
        pygame.display.set_caption("War")
        self.surface = pygame.display.set_mode(size)
        self.width, self.height = size

        self.clock = pygame.time.Clock()
        self.fps = fps
        self.speed = speed  # time to wait between each card
        self.remaining_pause = 0  # used to pause the mainloop

        self.rounds = 0
        self.winner = None

        self.running = True
        self.auto_close = close

        self.black_deck, self.red_deck = self.create_decks()
        self.black_pile, self.red_pile = self.create_pile()

    def create_pile(self) -> tuple[Pile, Pile]:
        pile_black = Pile(
            [],
            (self.width // 2 - Card.w // 2, self.height // 2 - Card.h),
            pygame.Rect(14 * Card.w, 2 * Card.h, Card.w, Card.h),
        )
        pile_red = Pile(
            [],
            (self.width // 2 - Card.w // 2, self.height // 2),
            pygame.Rect(14 * Card.w, 3 * Card.h, Card.w, Card.h),
        )
        return pile_black, pile_red

    def create_decks(self) -> tuple[Pile, Pile]:
        # generate the cards and shuffle them
        cards = []
        for row in range(4):
            for col in range(13):
                value = 14 if col + 1 == 1 else col + 1  # 14 for aces
                image = (col * Card.w, row * Card.h, Card.w, Card.h)
                cards.append(Card(value, image))
        random.shuffle(cards)

        # split the cards into two Pile object
        deck_black = Pile(
            cards[len(cards) // 2 :],
            (0, 0),
            pygame.Rect(14 * Card.w, 2 * Card.h, Card.w, Card.h),
        )
        deck_red = Pile(
            cards[: len(cards) // 2],
            (self.width - Card.w, self.height - Card.h),
            pygame.Rect(14 * Card.w, 3 * Card.h, Card.w, Card.h),
        )

        return deck_black, deck_red

    def pause(self, seconds: int = None) -> bool:
        if seconds:
            self.remaining_pause = seconds * self.fps
        if self.remaining_pause:
            self.remaining_pause -= 1
            return True
        return False

    def give_or_battle(self) -> None:
        try:
            # insufficient number of cards on pile
            if not (self.black_pile.even() and self.red_pile.even()):
                self.black_pile.cards.append(self.black_deck.cards.pop(0))
                self.red_pile.cards.append(self.red_deck.cards.pop(0))

            # equality
            elif self.black_pile.last().value == self.red_pile.last().value:
                self.rounds += 1
                self.black_pile.cards.append(self.black_deck.cards.pop(0))
                self.red_pile.cards.append(self.red_deck.cards.pop(0))

            # black win
            elif self.black_pile.last().value > self.red_pile.last().value:
                self.rounds += 1
                cards = self.black_pile.cards + self.red_pile.cards
                random.shuffle(cards)
                self.black_deck.cards.extend(cards)
                self.black_pile.cards, self.red_pile.cards = [], []

            # red win
            elif self.black_pile.last().value < self.red_pile.last().value:
                self.rounds += 1
                cards = self.red_pile.cards + self.black_pile.cards
                random.shuffle(cards)
                self.red_deck.cards.extend(cards)
                self.black_pile.cards, self.red_pile.cards = [], []

        except IndexError:  # happen when no card to add
            self.black_deck.cards.extend(self.black_pile.cards)
            self.red_deck.cards.extend(self.red_pile.cards)
            self.black_pile.cards.clear()
            self.red_pile.cards.clear()
        self.pause(self.speed)

    def render_decks(self):
        for deck in (self.black_deck, self.red_deck):
            font = pygame.font.SysFont("aria", Card.w // 3)
            label = font.render(f"{len(deck.cards)}", 1, (0, 0, 0))

            # create the rect for the label and the square
            label_rect = label.get_rect()
            square = pygame.Rect(0, 0, 40, 40)

            # draw the deck
            deck_rect = self.surface.blit(Card.sprite, deck.pos, deck.image)
            # center the label and the square to the deck
            label_rect.center = deck_rect.center
            square.center = deck_rect.center
            # draw the square and the label
            pygame.draw.rect(self.surface, "white", square, border_radius=10)
            pygame.draw.rect(self.surface, "black", square, 4, 10)
            self.surface.blit(label, (label_rect.topleft))

    def render_piles(self):
        for pile in (self.red_pile, self.black_pile):
            if not pile.cards:
                continue
            if len(pile.cards) % 2:
                self.surface.blit(Card.sprite, pile.pos, pile.cards[-1].image)
            else:  # render cards face down
                self.surface.blit(Card.sprite, pile.pos, pile.image)

    def render_victory(self):
        font = pygame.font.SysFont("aria", Card.w // 4)
        text = f"{self.winner} has won after {self.rounds} rounds"
        label = font.render(text, 1, (0, 0, 0))

        # retrieve rect
        label_rect = label.get_rect()
        square = label.get_rect().copy()
        square.width += 20
        square.height += 20
        # center them
        label_rect.center = self.surface.get_rect().center
        square.center = label_rect.center
        # render them
        pygame.draw.rect(self.surface, "white", square, border_radius=10)
        pygame.draw.rect(self.surface, "black", square, 4, border_radius=10)
        self.surface.blit(label, label_rect)

    def check_victory(self):
        if len(self.red_deck.cards) == 52:
            self.winner = "Red"
        if len(self.black_deck.cards) == 52:
            self.winner = "Black"
        if self.winner and self.auto_close:
            self.running = False

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # exit
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # exit with escape
                    self.running = False

    def run(self) -> int:
        pygame.init()
        while self.running:
            self.clock.tick(self.fps)
            self.handle_events()

            # display end screen
            if self.winner:
                self.render_victory()
                pygame.display.update()
                continue

            # hold the execution for a certain time
            if self.pause():
                continue

            # simulate the game
            self.give_or_battle()
            self.check_victory()

            # render
            self.surface.fill("#FC8EAC")
            self.render_decks()
            self.render_piles()
            pygame.display.update()

        return self.rounds


def main():
    game = Game(
        speed=SPEED,
        fps=FPS,
        close=True,
    )
    game.run()


if __name__ == "__main__":
    main()
