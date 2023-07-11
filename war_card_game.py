import pathlib
import random

import pygame


FPS: int = 120
SPEED: float = 0  # time between each, card must be non negative
SPRITES = pathlib.Path(__file__).parent / "CuteCards - asset pack" / "CuteCards.png"


class Card:
    width = 100
    height = 144
    sprite = pygame.image.load(SPRITES)

    def __init__(self, value: int, image: pygame.Rect):
        self.value = value
        self.image = image  # portion of SPRITES to display


class Pile:
    def __init__(self, cards: list[Card], pos: tuple[int, int], image: pygame.Rect):
        self.cards = cards
        self.image = image  # portion of SPRITES to display
        self.pos = pos


class Game:
    def __init__(
        self,
        fps: int = 60,
        size: tuple[int, int] = (3 * Card.width, 2 * Card.height),
        speed: int = 0.5,
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

        self.black_deck, self.red_deck = self.create_decks()
        self.black_pile, self.red_pile = self.create_pile()

    def create_pile(self) -> tuple[Pile, Pile]:
        pile_black = Pile(
            [],
            (self.width // 2 - Card.width // 2, self.height // 2 - Card.height),
            pygame.Rect(14 * Card.width, 2 * Card.height, Card.width, Card.height),
        )
        pile_red = Pile(
            [],
            (self.width // 2 - Card.width // 2, self.height // 2),
            pygame.Rect(14 * Card.width, 3 * Card.height, Card.width, Card.height),
        )
        return pile_black, pile_red

    def create_decks(self) -> tuple[Pile, Pile]:
        # generate the cards and shuffle them
        cards = []
        for row in range(4):
            for col in range(13):
                value = 14 if col + 1 == 1 else col + 1  # 14 for aces
                image = (col * Card.width, row * Card.height, Card.width, Card.height)
                cards.append(Card(value, image))
        random.shuffle(cards)

        # split the cards into two Pile object
        deck_black = Pile(
            cards[len(cards) // 2 :],
            (0, 0),
            pygame.Rect(14 * Card.width, 2 * Card.height, Card.width, Card.height),
        )
        deck_red = Pile(
            cards[: len(cards) // 2],
            (self.width - Card.width, self.height - Card.height),
            pygame.Rect(14 * Card.width, 3 * Card.height, Card.width, Card.height),
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
            if not (len(self.black_pile.cards) % 2 and len(self.red_pile.cards) % 2):
                self.black_pile.cards.append(self.black_deck.cards.pop(0))
                self.red_pile.cards.append(self.red_deck.cards.pop(0))

            # equality
            elif self.black_pile.cards[-1].value == self.red_pile.cards[-1].value:
                self.rounds += 1
                # add more cards
                self.black_pile.cards.append(self.black_deck.cards.pop(0))
                self.red_pile.cards.append(self.red_deck.cards.pop(0))

            # black win
            elif self.black_pile.cards[-1].value > self.red_pile.cards[-1].value:
                self.rounds += 1
                # reinsert piles inside the winning game
                cards = self.red_pile.cards + self.black_pile.cards
                random.shuffle(cards)
                self.black_deck.cards.extend(cards)
                # clear piles
                self.black_pile.cards, self.red_pile.cards = [], []

            # red win
            elif self.black_pile.cards[-1].value < self.red_pile.cards[-1].value:
                self.rounds += 1
                # reinsert piles inside the winning game
                cards = self.red_pile.cards + self.black_pile.cards
                random.shuffle(cards)
                self.red_deck.cards.extend(cards)
                # clear piles
                self.black_pile.cards, self.red_pile.cards = [], []

        # happen when no card to add
        except IndexError:
            # shuffle piles into decks
            self.black_deck.cards = self.black_deck.cards + self.black_pile.cards
            self.red_deck.cards = self.red_deck.cards + self.red_pile.cards
            random.shuffle(self.black_deck.cards)
            random.shuffle(self.red_deck.cards)
            # clear both piles
            self.black_pile.cards, self.red_pile.cards = [], []

        self.pause(self.speed)

    def render_decks(self):
        for deck in (self.black_deck, self.red_deck):
            font = pygame.font.SysFont("aria", Card.width // 3)
            label = font.render(f"{len(deck.cards)}", 1, (0, 0, 0))

            # create the rect for the label and the square
            label_rect = label.get_rect()
            square_rect = pygame.Rect(0, 0, 40, 40)

            # draw the deck
            deck_rect = self.surface.blit(Card.sprite, deck.pos, deck.image)
            # center the label and the square to the deck
            label_rect.center = deck_rect.center
            square_rect.center = deck_rect.center
            # draw the square and the label
            pygame.draw.rect(self.surface, "white", square_rect, border_radius=10)
            pygame.draw.rect(self.surface, "black", square_rect, 4, 10)
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
        font = pygame.font.SysFont("aria", Card.width // 4)
        text = f"{self.winner} has won after {self.rounds} rounds"
        label = font.render(text, 1, (0, 0, 0))

        # retrieve rect
        label_rect = label.get_rect()
        square_rect = label.get_rect().copy()
        square_rect.width += 20
        square_rect.height += 20
        # center them
        label_rect.center = self.surface.get_rect().center
        square_rect.center = label_rect.center
        # render them
        pygame.draw.rect(self.surface, "white", square_rect, border_radius=10)
        pygame.draw.rect(self.surface, "black", square_rect, 4, border_radius=10)
        self.surface.blit(label, label_rect)  # replace the text in top of the rect

    def check_victory(self):
        if len(self.red_deck.cards) + len(self.red_pile.cards) == 0:
            self.winner = "Black"
        if len(self.black_deck.cards) + len(self.black_pile.cards) == 0:
            self.winner = "Red"

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # exit
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:  # exit with escape
                    self.running = False

    def run(self) -> int:
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


def main():
    pygame.init()
    game = Game(speed=SPEED, fps=FPS)
    game.run()


if __name__ == "__main__":
    main()
