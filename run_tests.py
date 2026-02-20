
import sys
import unittest
from unittest.mock import MagicMock

# Mock missing dependencies
sys.modules["watchdog"] = MagicMock()
sys.modules["watchdog.observers"] = MagicMock()
sys.modules["watchdog.events"] = MagicMock()
sys.modules["requests"] = MagicMock()
sys.modules["telegram"] = MagicMock()
sys.modules["telegram.error"] = MagicMock()
sys.modules["openai"] = MagicMock()
sys.modules["openai.resources"] = MagicMock()
sys.modules["openai.resources.chat"] = MagicMock()

# Mock specific imports that might be used
mock_observer = MagicMock()
sys.modules["watchdog.observers"].Observer = mock_observer

print("✅ Mocks installed for watchdog and requests")

# Now we can safely import our modules
# Add src to path
import os
sys.path.insert(0, os.path.abspath("src"))

# Import tests
# We will create these files next, but for now we'll discover them
if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = loader.discover("tests")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
