"""Category-specific semantic handlers.

These are an explicit POC shortcut. They do not implement general recognition.
"""
from lab.v3.handlers.heart import handle_heart
from lab.v3.handlers.messy import handle_messy
from lab.v3.handlers.plant import handle_plant
from lab.v3.handlers.rocket import handle_rocket
from lab.v3.handlers.rose import handle_rose
from lab.v3.handlers.teddy import handle_teddy

HANDLERS = {
    "heart": handle_heart,
    "rocket": handle_rocket,
    "teddy": handle_teddy,
    "plant": handle_plant,
    "rose": handle_rose,
    "messy_incomplete": handle_messy,
    "messy": handle_messy,
}
