from dataclasses import dataclass


@dataclass
class Track:
    url: str
    title: str
    duration: float | None = None
    origin: str = "Vídeo único"
    selected: bool = True
    output_name: str = ""

    def __post_init__(self):
        if not self.output_name:
            self.output_name = self.title
