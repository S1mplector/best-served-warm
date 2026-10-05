"""Tiny branching point for the placeholder cafe story loop."""

DIALOGUE = (
    ("A RAINY MORNING", "The bell rings softly above the door.",
     "The beans are fresh. The counter is ready.",
     "Someone is waiting for a warm cup."),
    ("A LITTLE WELCOME", "Choose a cup and a roast, then grind.",
     "Tamp gently. Watch the coffee flow.",
     "A little patience makes a lovely cup."),
    ("YOUR FIRST ORDER", "Mila would love a latte and a croissant.",
     "Her order is waiting beside the machine.",
     "Let's make something warm."),
)


class Dialogue:
    def __init__(self) -> None:
        self.page = 0
        self.revealed = 0.0

    @property
    def current(self) -> tuple[str, ...]:
        return DIALOGUE[self.page]

    @property
    def complete(self):
        return int(self.revealed) >= sum(map(len, self.current[1:]))

    @property
    def visible_lines(self):
        remaining = int(self.revealed)
        lines = []
        for line in self.current[1:]:
            lines.append(line[:max(0, remaining)])
            remaining -= len(line)
        return lines

    def update(self, dt):
        text = "".join(self.current[1:])
        old = int(self.revealed)
        self.revealed = min(len(text), self.revealed + dt * 32)
        return any(c.isalnum() for c in text[old:int(self.revealed)])

    @property
    def is_last_page(self) -> bool:
        return self.page == len(DIALOGUE) - 1

    def advance(self) -> bool:
        """Move forward; return True when the dialogue is complete."""
        if not self.complete:
            self.revealed = sum(map(len, self.current[1:]))
            return False
        if self.is_last_page:
            return True
        self.page += 1
        self.revealed = 0.0
        return False
