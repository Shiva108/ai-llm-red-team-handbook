#!/usr/bin/env python3
"""
Attack Pattern Registry

Manages registration, discovery, and retrieval of attack patterns.
Supports dynamic loading of pattern plugins.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterator, Type

from core.models import AttackCategory, InjectionPoint

if TYPE_CHECKING:
    from .base import BaseAttackPattern

logger = logging.getLogger(__name__)


class PatternRegistry:
    """
    Central registry for attack patterns.

    Provides pattern discovery, registration, and retrieval functionality.
    Supports both built-in patterns and custom plugin patterns.
    """

    _instance: PatternRegistry | None = None
    _patterns: dict[str, Type[BaseAttackPattern]]
    _initialized: bool = False

    def __new__(cls) -> PatternRegistry:
        """Singleton pattern for global registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._patterns = {}
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the registry."""
        if not self._initialized:
            self._patterns = {}
            self._initialized = True

    def register(
        self,
        pattern_class: Type[BaseAttackPattern],
        pattern_id: str | None = None,
    ) -> None:
        """
        Register an attack pattern class.

        Args:
            pattern_class: The pattern class to register
            pattern_id: Optional custom ID (uses class pattern_id by default)
        """
        pid = pattern_id or pattern_class.pattern_id
        if pid in self._patterns:
            logger.warning(f"Overwriting existing pattern: {pid}")
        self._patterns[pid] = pattern_class
        logger.debug(f"Registered pattern: {pid}")

    def unregister(self, pattern_id: str) -> bool:
        """
        Unregister a pattern by ID.

        Args:
            pattern_id: The pattern ID to unregister

        Returns:
            True if pattern was removed, False if not found
        """
        if pattern_id in self._patterns:
            del self._patterns[pattern_id]
            logger.debug(f"Unregistered pattern: {pattern_id}")
            return True
        return False

    def get(self, pattern_id: str) -> Type[BaseAttackPattern] | None:
        """
        Get a pattern class by ID.

        Args:
            pattern_id: The pattern ID to retrieve

        Returns:
            The pattern class or None if not found
        """
        return self._patterns.get(pattern_id)

    def get_instance(
        self,
        pattern_id: str,
        **kwargs: Any,
    ) -> BaseAttackPattern | None:
        """
        Get an instantiated pattern by ID.

        Args:
            pattern_id: The pattern ID to retrieve
            **kwargs: Arguments passed to pattern constructor

        Returns:
            Instantiated pattern or None if not found
        """
        pattern_class = self.get(pattern_id)
        if pattern_class:
            return pattern_class(**kwargs)
        return None

    def list_all(self) -> list[str]:
        """List all registered pattern IDs."""
        return list(self._patterns.keys())

    def list_by_category(self, category: AttackCategory) -> list[str]:
        """
        List pattern IDs by category.

        Args:
            category: The attack category to filter by

        Returns:
            List of pattern IDs in the specified category
        """
        return [
            pid
            for pid, pattern_class in self._patterns.items()
            if pattern_class.category == category
        ]

    def get_all_by_category(
        self,
        category: AttackCategory,
        **kwargs: Any,
    ) -> list[BaseAttackPattern]:
        """
        Get all instantiated patterns for a category.

        Args:
            category: The attack category to filter by
            **kwargs: Arguments passed to pattern constructors

        Returns:
            List of instantiated patterns
        """
        return [
            pattern_class(**kwargs)
            for pattern_class in self._patterns.values()
            if pattern_class.category == category
        ]

    def get_applicable(
        self,
        injection_point: InjectionPoint,
        **kwargs: Any,
    ) -> list[BaseAttackPattern]:
        """
        Get all patterns applicable to an injection point.

        Args:
            injection_point: The injection point to check against
            **kwargs: Arguments passed to pattern constructors

        Returns:
            List of applicable pattern instances
        """
        applicable = []
        for pattern_class in self._patterns.values():
            instance = pattern_class(**kwargs)
            if instance.is_applicable(injection_point):
                applicable.append(instance)
        return applicable

    def iter_patterns(self, **kwargs: Any) -> Iterator[BaseAttackPattern]:
        """
        Iterate over all pattern instances.

        Args:
            **kwargs: Arguments passed to pattern constructors

        Yields:
            Pattern instances
        """
        for pattern_class in self._patterns.values():
            yield pattern_class(**kwargs)

    def load_builtin_patterns(self) -> int:
        """
        Load all built-in patterns from the patterns package.

        Returns:
            Number of patterns loaded
        """
        from . import advanced, direct, indirect

        count = 0

        # Load direct injection patterns
        for module in [direct]:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "pattern_id")
                    and attr_name != "BaseAttackPattern"
                    and not attr_name.startswith("_")
                ):
                    try:
                        from .base import BaseAttackPattern

                        if issubclass(attr, BaseAttackPattern) and attr is not BaseAttackPattern:
                            self.register(attr)
                            count += 1
                    except TypeError:
                        pass

        # Load indirect injection patterns
        for module in [indirect]:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "pattern_id")
                    and attr_name != "BaseAttackPattern"
                    and not attr_name.startswith("_")
                ):
                    try:
                        from .base import BaseAttackPattern

                        if issubclass(attr, BaseAttackPattern) and attr is not BaseAttackPattern:
                            self.register(attr)
                            count += 1
                    except TypeError:
                        pass

        # Load advanced patterns
        for module in [advanced]:
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and hasattr(attr, "pattern_id")
                    and attr_name != "BaseAttackPattern"
                    and not attr_name.startswith("_")
                ):
                    try:
                        from .base import BaseAttackPattern

                        if issubclass(attr, BaseAttackPattern) and attr is not BaseAttackPattern:
                            self.register(attr)
                            count += 1
                    except TypeError:
                        pass

        logger.info(f"Loaded {count} built-in patterns")
        return count

    def load_plugin(self, plugin_path: str | Path) -> int:
        """
        Load patterns from a plugin file.

        Args:
            plugin_path: Path to the plugin Python file

        Returns:
            Number of patterns loaded from the plugin
        """
        from .base import BaseAttackPattern

        path = Path(plugin_path)
        if not path.exists():
            raise FileNotFoundError(f"Plugin file not found: {plugin_path}")

        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load plugin: {plugin_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        count = 0
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseAttackPattern)
                and attr is not BaseAttackPattern
            ):
                self.register(attr)
                count += 1

        logger.info(f"Loaded {count} patterns from plugin: {plugin_path}")
        return count

    def load_plugins_from_directory(self, directory: str | Path) -> int:
        """
        Load all plugin patterns from a directory.

        Args:
            directory: Path to the plugins directory

        Returns:
            Total number of patterns loaded
        """
        path = Path(directory)
        if not path.exists():
            logger.warning(f"Plugin directory not found: {directory}")
            return 0

        total = 0
        for plugin_file in path.glob("*.py"):
            if plugin_file.name.startswith("_"):
                continue
            try:
                total += self.load_plugin(plugin_file)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file}: {e}")

        return total

    def clear(self) -> None:
        """Clear all registered patterns."""
        self._patterns.clear()
        logger.debug("Pattern registry cleared")

    def __len__(self) -> int:
        return len(self._patterns)

    def __contains__(self, pattern_id: str) -> bool:
        return pattern_id in self._patterns

    def __repr__(self) -> str:
        return f"PatternRegistry(patterns={len(self._patterns)})"


# Global registry instance
registry = PatternRegistry()


def register_pattern(pattern_class: Type[BaseAttackPattern]) -> Type[BaseAttackPattern]:
    """
    Decorator to register a pattern class.

    Usage:
        @register_pattern
        class MyCustomPattern(BaseAttackPattern):
            pattern_id = "my_custom_pattern"
            ...
    """
    registry.register(pattern_class)
    return pattern_class


def get_pattern(pattern_id: str, **kwargs: Any) -> BaseAttackPattern | None:
    """Convenience function to get a pattern instance."""
    return registry.get_instance(pattern_id, **kwargs)


def list_patterns() -> list[str]:
    """Convenience function to list all pattern IDs."""
    return registry.list_all()


def get_patterns_for_category(
    category: AttackCategory,
    **kwargs: Any,
) -> list[BaseAttackPattern]:
    """Convenience function to get patterns by category."""
    return registry.get_all_by_category(category, **kwargs)
