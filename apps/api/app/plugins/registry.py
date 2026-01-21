"""
Plugin registry for discovering and managing plugins.

The registry provides a central location for:
- Registering model plugins
- Registering preprocessing methods
- Discovering plugins at startup
- Retrieving plugins by slug or category
"""

import importlib
import pkgutil
from typing import Dict, List, Optional, Type

from app.plugins.base import BaseModelPlugin, ProblemType


class PluginRegistry:
    """
    Central registry for all plugins.

    Maintains separate registries for model plugins and preprocessing methods.
    Supports auto-discovery of plugins in designated packages.
    """

    _model_plugins: Dict[str, Type[BaseModelPlugin]] = {}
    _preprocessing_methods: Dict[str, dict] = {}
    _initialized: bool = False

    @classmethod
    def register_model(cls, plugin_class: Type[BaseModelPlugin]) -> None:
        """
        Register a model plugin.

        Args:
            plugin_class: The plugin class to register
        """
        if not hasattr(plugin_class, "slug"):
            raise ValueError(f"Plugin {plugin_class.__name__} must define a 'slug' attribute")

        cls._model_plugins[plugin_class.slug] = plugin_class

    @classmethod
    def register_preprocessing(cls, method_config: dict) -> None:
        """
        Register a preprocessing method.

        Args:
            method_config: Configuration dict with slug, name, category, etc.
        """
        if "slug" not in method_config:
            raise ValueError("Preprocessing method must have a 'slug' key")

        cls._preprocessing_methods[method_config["slug"]] = method_config

    @classmethod
    def get_model(cls, slug: str) -> Optional[Type[BaseModelPlugin]]:
        """Get a model plugin by slug."""
        cls._ensure_initialized()
        return cls._model_plugins.get(slug)

    @classmethod
    def get_all_models(cls) -> List[Type[BaseModelPlugin]]:
        """Get all registered model plugins."""
        cls._ensure_initialized()
        return list(cls._model_plugins.values())

    @classmethod
    def get_models_by_problem_type(
        cls, problem_type: ProblemType
    ) -> List[Type[BaseModelPlugin]]:
        """Get model plugins that support the given problem type."""
        cls._ensure_initialized()
        return [
            plugin
            for plugin in cls._model_plugins.values()
            if problem_type in plugin.problem_types
        ]

    @classmethod
    def get_preprocessing(cls, slug: str) -> Optional[dict]:
        """Get a preprocessing method by slug."""
        cls._ensure_initialized()
        return cls._preprocessing_methods.get(slug)

    @classmethod
    def get_all_preprocessing(cls) -> List[dict]:
        """Get all registered preprocessing methods."""
        cls._ensure_initialized()
        return list(cls._preprocessing_methods.values())

    @classmethod
    def get_preprocessing_by_category(cls, category: str) -> List[dict]:
        """Get preprocessing methods in a category."""
        cls._ensure_initialized()
        return [
            method
            for method in cls._preprocessing_methods.values()
            if method.get("category") == category
        ]

    @classmethod
    def discover_plugins(cls) -> None:
        """
        Auto-discover and register all plugins.

        This scans the plugins.models and plugins.preprocessing packages
        for plugin definitions and registers them.
        """
        if cls._initialized:
            return

        # Discover model plugins
        cls._discover_model_plugins()

        # Discover preprocessing methods
        cls._discover_preprocessing_methods()

        cls._initialized = True

    @classmethod
    def _discover_model_plugins(cls) -> None:
        """Discover and register model plugins from plugins.models package."""
        try:
            import app.plugins.models as models_pkg

            for importer, modname, ispkg in pkgutil.iter_modules(models_pkg.__path__):
                if modname.startswith("_"):
                    continue

                try:
                    module = importlib.import_module(f"app.plugins.models.{modname}")

                    # Look for plugin class in module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (
                            isinstance(attr, type)
                            and issubclass(attr, BaseModelPlugin)
                            and attr is not BaseModelPlugin
                            and hasattr(attr, "slug")
                        ):
                            cls.register_model(attr)
                except Exception as e:
                    print(f"Error loading model plugin {modname}: {e}")

        except ImportError:
            pass  # models package doesn't exist yet

    @classmethod
    def _discover_preprocessing_methods(cls) -> None:
        """Discover and register preprocessing methods."""
        try:
            from app.plugins.preprocessing.registry import PREPROCESSING_METHODS

            for method in PREPROCESSING_METHODS:
                cls.register_preprocessing(method)
        except ImportError:
            pass  # preprocessing registry doesn't exist yet

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure plugins have been discovered."""
        if not cls._initialized:
            cls.discover_plugins()

    @classmethod
    def reset(cls) -> None:
        """Reset the registry (mainly for testing)."""
        cls._model_plugins = {}
        cls._preprocessing_methods = {}
        cls._initialized = False


# Convenience functions
def get_model_plugin(slug: str) -> Optional[Type[BaseModelPlugin]]:
    """Get a model plugin by slug."""
    return PluginRegistry.get_model(slug)


def get_all_model_plugins() -> List[Type[BaseModelPlugin]]:
    """Get all model plugins."""
    return PluginRegistry.get_all_models()


def get_model_plugins_by_problem_type(
    problem_type: str
) -> List[Type[BaseModelPlugin]]:
    """Get model plugins that support a problem type."""
    pt = ProblemType(problem_type)
    return PluginRegistry.get_models_by_problem_type(pt)


def get_preprocessing_method(slug: str) -> Optional[dict]:
    """Get a preprocessing method by slug."""
    return PluginRegistry.get_preprocessing(slug)


def get_all_preprocessing_methods() -> List[dict]:
    """Get all preprocessing methods."""
    return PluginRegistry.get_all_preprocessing()


def get_preprocessing_methods_by_category(category: str) -> List[dict]:
    """Get preprocessing methods in a category."""
    return PluginRegistry.get_preprocessing_by_category(category)
