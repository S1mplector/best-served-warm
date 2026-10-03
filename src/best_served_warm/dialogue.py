"""Tiny branching point for the placeholder cafe story loop."""

DIALOGUE = (
    ("A RAINY MORNING", "Lorem ipsum dolor sit amet, consectetur",
     "adipiscing elit. A bell rings above the door.",
     "Someone is waiting for a warm cup."),
    ("A LITTLE WELCOME", "Lorem ipsum dolor sit amet, consectetur",
     "adipiscing elit. The kettle begins to sing.",
     "Outside, the rain turns soft and silver."),
    ("YOUR FIRST ORDER", "Lorem ipsum dolor sit amet, consectetur",
     "adipiscing elit. There is time to make",
     "something lovely, one cup at a time."),
)


class Dialogue:
    def __init__(self) -> None:
        self.page = 0

    @property
    def current(self) -> tuple[str, ...]:
        return DIALOGUE[self.page]

    @property
    def is_last_page(self) -> bool:
        return self.page == len(DIALOGUE) - 1

    def advance(self) -> bool:
        """Move forward; return True when the dialogue is complete."""
        if self.is_last_page:
            return True
        self.page += 1
        return False
