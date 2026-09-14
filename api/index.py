import os
import sys

# Ensure repository root is in sys.path for Vercel serverless runtime
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from resolvecall.web.app import app

# Export app for Vercel ASGI runner
__all__ = ["app"]
