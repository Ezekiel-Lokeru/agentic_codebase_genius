import typing
import sys

# Ensure override is available (Python 3.12+)
# This handles cases where older Python versions might be used unexpectedly
if not hasattr(typing, "override"):
    # For Python < 3.12, provide a no-op decorator
    def override(func=None):
        """No-op decorator for Python < 3.12 compatibility"""
        return func
    
    typing.override = override

# Also patch sys.modules to ensure all future imports get the patched version
if 'typing' in sys.modules:
    sys.modules['typing'].override = getattr(typing, 'override')
