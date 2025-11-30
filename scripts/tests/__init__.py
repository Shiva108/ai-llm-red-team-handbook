# file: tests/__init__.py

from typing import List, Type

from models import BaseTest
from .test_prompt_injection import PromptInjectionTest
from .test_data_exposure import DataExposureTest
from .test_tool_misuse import ToolMisuseTest
from .test_integrity import IntegrityTest
from .test_safety_bypass import SafetyBypassTest
from .test_fuzzing import FuzzingTest


def get_all_tests() -> List[BaseTest]:
    """Instantiate all test classes."""
    test_classes: List[Type[BaseTest]] = [
        PromptInjectionTest,
        DataExposureTest,
        ToolMisuseTest,
        IntegrityTest,
        SafetyBypassTest,
        FuzzingTest,
    ]
    return [cls() for cls in test_classes]
