# Importamos los subpaquetes
from . import app
# from . import dialogs  <-- Cuando lo crees, solo descomentas o añades
# from . import components

# Traemos el contenido de los subpaquetes al nivel de ui
from .app import *
# from .dialogs import *

# Sumamos todos los __all__ de los subpaquetes para que ui tenga el suyo propio
__all__ = []
__all__.extend(app.__all__)
# __all__.extend(dialogs.__all__)