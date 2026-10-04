"""Tiny branching point for the placeholder cafe story loop."""

DIALOGUE = (
    ("A RAINY MORNING", "Lorem ipsum dolor sit amet, consectetur",
     "adipiscing elit. A bell rings above the door.",
     "Someone is waiting for a warm cup."),
    ("A LITTLE WELCOME", "Lorem ipsum dolor sit amet, consectetur",
     "adipiscing elit. The kettle begins to sing.",
     "Outside, the rain turns soft and silver."),
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
