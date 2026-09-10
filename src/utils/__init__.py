"""RetailPulse utility package.

Keep package initialization lightweight so importing submodules such as
``src.utils.config`` or ``src.utils.logger`` cannot create circular imports.
Import utilities explicitly from their defining modules.
"""

__all__ = []
