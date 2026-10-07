"""Dialogue-only opening chapter for the cafe story."""

from textwrap import wrap

# Each entry is a speaker turn. Explicit newlines keep options and sound cues
# on separate rows; all other wrapping uses nearly the full dialogue width.
STORY = (
    ("YOU", "START!\n*Blinking animation.* Yawning, rubbing our eyes..."),
    ("YOU", "No one told me that being a barista meant slowly growing immune to the effects of caffeine... Maybe you can breathe caffeine in?"),
    ("YOU", "I swear I don't drink more than 4 cups a day... or 4 mugs? Today I'll need more... Taking the night train from my parents' house was not a good idea..."),
    ("LENA", "HEY! *Waves in my face.*\nFrom earth to (insert name).\nI need to brew, chop chop!"),
    ("YOU", "I was always given the nasty job of cleaning the espresso machine... Ground coffee always got under my nail beds... I just walked towards the sink without arguing..."),
    ("YOU", "*Mini game starts.*\n*Mini game makes the player fail on purpose.*"),
    ("YOU", "Just to clarify... that was NOT my fault."),
    ("LENA", "Hey... Is everything OK?"),
    ("OPTIONS", "> I'm tired... I had to come back to town late at night. (Not a real option.)\n> I'm fine, what are you talking about?"),
    ("YOU", "I'm okay... what do you mean?"),
    ("LENA", "I was just worried! Let me know if there's anything I can help you with! *Runs away.*"),
    ("YOU", "Liar... *Mini game continues.* And the sink... *Dish washing mini game starts.*"),
    ("YOU", "*Bell rings in the cafe.*\n*Sniffing sounds.*"),
    ("MRS HEATHER", "Why has the coffee not been brewed yet?"),
    ("YOU", "I make the mistake of looking back instead of ignoring her..."),
    ("MRS HEATHER", "(Insert name), we make our first cup of coffee ready before when?"),
    ("YOU", "Before 6..."),
    ("MRS HEATHER", "And what time is it?"),
    ("YOU", "I glance at the pendulum clock on the freshly painted wall... 6.23."),
    ("YOU", "Not 6... But ma'am..."),
    ("MRS HEATHER", "Just scoot!"),
    ("YOU", "*Aggressive dish washing sounds.*"),
    ("MRS HEATHER", "And fix those labels. What is a cocoa infused chocolate oat cookie? It's a goddamn chocolate chip!"),
    ("LENA", "But stuff sells way more when we name it like that!"),
    ("MRS HEATHER", "Chocolate chip has been around for centuries... Don't fix what's not broken..."),
    ("LENA", "Humph..."),
    ("YOU", "I understood her. New stuff scared me too... But choosing to leave my hometown was an easy change to make my mind up on..."),
    ("YOU", "The sweet smell in the cafe got even stronger as my old coworker opened the oven to take out today's cake. A simple butter and vanilla."),
    ("YOU", "The dim light of the counter and the smell was almost making up for the amount of dish washing this job required..."),
    ("YOU", "The back door of the kitchen opens slightly... At such a slow speed that I wouldn't have recognized it if the light of the morning sun didn't slip through the storage room into my work space here in the kitchen..."),
    ("SAM", "Shhh..."),
    ("OPTIONS", "> Silently warn about the manager\n> Stay put"),
    ("YOU", "He started hanging his coat on the wall while taking off his shoulder bag to rest it on the wooden floor..."),
    ("YOU", "*Creeaaakkkk!*\nThe manager turns around to lock eyes with him.\n*Silence.*"),
    ("MRS HEATHER", "Apron. Sink."),
    ("SAM", "Yes ma'am."),
    ("YOU", "Sounds of tilling at the cash register mixed with an overflowing sink and the smell of freshly ground coffee filled the entire place."),
    ("YOU", "The doors opened at 06.30 to a new day that was none other than a script repeating itself... Customer, pie, usual, tea, clean, the simple ritual..."),
    ("YOU", "But everything was on the brink of change that day... September 7th... And no one had a clue..."),
)

LINE_WIDTH = 50
ROWS_PER_PAGE = 3


def _make_pages() -> tuple[tuple[str, ...], ...]:
    pages: list[tuple[str, ...]] = []
    for speaker, text in STORY:
        lines: list[str] = []
        for row in text.splitlines():
            lines.extend(wrap(row, width=LINE_WIDTH, break_long_words=False,
                              break_on_hyphens=False) or [""])
        for offset in range(0, len(lines), ROWS_PER_PAGE):
            body = lines[offset:offset + ROWS_PER_PAGE]
            pages.append((speaker, *body, *("",) * (ROWS_PER_PAGE - len(body))))
    return tuple(pages)


DIALOGUE = _make_pages()


class Dialogue:
    def __init__(self) -> None:
        self.page = 0
        self.revealed = 0.0

    @property
    def current(self) -> tuple[str, ...]:
        return DIALOGUE[self.page]

    @property
    def complete(self) -> bool:
        return int(self.revealed) >= sum(map(len, self.current[1:]))

    @property
    def visible_lines(self) -> tuple[str, ...]:
        remaining = int(self.revealed)
        lines = []
        for line in self.current[1:]:
            lines.append(line[:max(0, remaining)])
            remaining -= len(line)
        return tuple(lines)

    def update(self, dt: float) -> bool:
        text = "".join(self.current[1:])
        old = int(self.revealed)
        self.revealed = min(len(text), self.revealed + dt * 32)
        return any(c.isalnum() for c in text[old:int(self.revealed)])

    @property
    def is_last_page(self) -> bool:
        return self.page == len(DIALOGUE) - 1

    def advance(self) -> bool:
        """Reveal or advance a page; keep the final page visible when finished."""
        if not self.complete:
            self.revealed = sum(map(len, self.current[1:]))
            return False
        if self.is_last_page:
            return True
        self.page += 1
        self.revealed = 0.0
        return False
