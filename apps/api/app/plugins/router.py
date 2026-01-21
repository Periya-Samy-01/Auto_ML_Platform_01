"""
Plugin API endpoints.

Provides REST API for fetching plugin information for the Playground.
"""

from typing import Any, List, Optional, Union

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.plugins.registry import (
    PluginRegistry,
    get_model_plugin,
    get_all_model_plugins,
    get_model_plugins_by_problem_type,
)
from app.plugins.base import ProblemType
from app.plugins.preprocessing import (
    PREPROCESSING_CATEGORIES,
    get_all_methods,
    get_method,
    get_methods_by_category,
)
from app.plugins.shared.constants import (
    METRIC_DEFINITIONS,
    PLOT_DEFINITIONS,
    get_metrics_for_problem_type,
    get_plots_for_problem_type,
)

router = APIRouter(prefix="/plugins", tags=["plugins"])


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class ModelPluginSummary(BaseModel):
    """Summary of a model plugin for listing."""
    slug: str
    name: str
    description: str
    icon: str
    problemTypes: List[str]
    category: str
    bestFor: Optional[str] = None


class HyperparameterFieldResponse(BaseModel):
    """Hyperparameter field schema."""
    key: str
    name: str
    type: str
    default: Optional[Union[str, int, float, bool, None]] = None
    description: str = ""
    min: Optional[float] = None
    max: Optional[float] = None
    step: Optional[float] = None
    nullable: bool = False
    nullLabel: str = "Auto"
    options: Optional[List[dict]] = None
    required: bool = True


class HyperparametersResponse(BaseModel):
    """Hyperparameters schema."""
    main: List[dict]
    advanced: List[dict]


class CapabilitiesResponse(BaseModel):
    """Model capabilities for downstream nodes."""
    supportedMetrics: List[str]
    defaultMetrics: List[str]
    supportedPlots: List[str]
    defaultPlots: List[str]


class ModelPluginDetail(BaseModel):
    """Detailed model plugin information."""
    slug: str
    name: str
    description: str
    icon: str
    problemTypes: List[str]
    category: str
    bestFor: Optional[str] = None
    hyperparameters: HyperparametersResponse
    capabilities: Optional[CapabilitiesResponse] = None


class PreprocessingMethodResponse(BaseModel):
    """Preprocessing method information."""
    slug: str
    name: str
    description: str
    category: str
    appliesTo: List[str]
    parameters: List[dict]


class PreprocessingCategoryResponse(BaseModel):
    """Preprocessing category information."""
    key: str
    name: str
    description: str
    icon: str


class MetricDefinitionResponse(BaseModel):
    """Metric definition information."""
    key: str
    name: str
    description: str
    category: str
    higherIsBetter: bool
    appliesTo: List[str]
    cost: int


class PlotDefinitionResponse(BaseModel):
    """Plot definition information."""
    key: str
    name: str
    description: str
    category: str
    appliesTo: List[str]
    modelCategories: List[str]
    cost: int


class PluginsListResponse(BaseModel):
    """Combined plugins list response."""
    models: List[ModelPluginSummary]
    preprocessing: List[PreprocessingMethodResponse]


# =============================================================================
# MODEL PLUGIN ENDPOINTS
# =============================================================================

@router.get("", response_model=PluginsListResponse)
async def list_plugins(
    problem_type: Optional[str] = Query(None, description="Filter by problem type")
):
    """
    List all available plugins.

    Returns both model plugins and preprocessing methods.
    Optionally filter models by problem type.
    """
    # Ensure plugins are discovered
    PluginRegistry.discover_plugins()

    # Get model plugins
    if problem_type:
        try:
            pt = ProblemType(problem_type)
            model_plugins = get_model_plugins_by_problem_type(problem_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid problem type: {problem_type}. Must be one of: classification, regression, clustering"
            )
    else:
        model_plugins = get_all_model_plugins()

    models = [
        ModelPluginSummary(
            slug=p.slug,
            name=p.name,
            description=p.description,
            icon=p.icon,
            problemTypes=[pt.value for pt in p.problem_types],
            category=p.category.value,
            bestFor=p.best_for if hasattr(p, 'best_for') else None,
        )
        for p in model_plugins
    ]

    # Get preprocessing methods
    preprocessing = [
        PreprocessingMethodResponse(
            slug=m["slug"],
            name=m["name"],
            description=m["description"],
            category=m["category"],
            appliesTo=m["applies_to"],
            parameters=m["parameters"],
        )
        for m in get_all_methods()
    ]

    return PluginsListResponse(models=models, preprocessing=preprocessing)


@router.get("/models", response_model=List[ModelPluginSummary])
async def list_model_plugins(
    problem_type: Optional[str] = Query(None, description="Filter by problem type")
):
    """
    List all model plugins.

    Optionally filter by problem type (classification, regression, clustering).
    """
    PluginRegistry.discover_plugins()

    if problem_type:
        try:
            plugins = get_model_plugins_by_problem_type(problem_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid problem type: {problem_type}"
            )
    else:
        plugins = get_all_model_plugins()

    return [
        ModelPluginSummary(
            slug=p.slug,
            name=p.name,
            description=p.description,
            icon=p.icon,
            problemTypes=[pt.value for pt in p.problem_types],
            category=p.category.value,
            bestFor=p.best_for if hasattr(p, 'best_for') else None,
        )
        for p in plugins
    ]


@router.get("/models/{slug}", response_model=ModelPluginDetail)
async def get_model_plugin_detail(
    slug: str,
    problem_type: Optional[str] = Query(None, description="Problem type for capabilities")
):
    """
    Get detailed information about a model plugin.

    Includes hyperparameter schema and capabilities.
    If problem_type is provided, capabilities will be filtered for that type.
    """
    PluginRegistry.discover_plugins()

    plugin = get_model_plugin(slug)
    if plugin is None:
        raise HTTPException(status_code=404, detail=f"Model plugin not found: {slug}")

    # Get hyperparameters
    hyperparameters = plugin.get_hyperparameters()

    # Get capabilities for the specified or first problem type
    capabilities = None
    if problem_type:
        try:
            pt = ProblemType(problem_type)
            if pt in plugin.problem_types:
                caps = plugin.get_capabilities(pt)
                capabilities = CapabilitiesResponse(
                    supportedMetrics=caps.supported_metrics,
                    defaultMetrics=caps.default_metrics,
                    supportedPlots=caps.supported_plots,
                    defaultPlots=caps.default_plots,
                )
        except ValueError:
            pass
    elif plugin.problem_types:
        pt = plugin.problem_types[0]
        caps = plugin.get_capabilities(pt)
        capabilities = CapabilitiesResponse(
            supportedMetrics=caps.supported_metrics,
            defaultMetrics=caps.default_metrics,
            supportedPlots=caps.supported_plots,
            defaultPlots=caps.default_plots,
        )

    return ModelPluginDetail(
        slug=plugin.slug,
        name=plugin.name,
        description=plugin.description,
        icon=plugin.icon,
        problemTypes=[pt.value for pt in plugin.problem_types],
        category=plugin.category.value,
        bestFor=plugin.best_for if hasattr(plugin, 'best_for') else None,
        hyperparameters=HyperparametersResponse(
            main=hyperparameters.to_dict()["main"],
            advanced=hyperparameters.to_dict()["advanced"],
        ),
        capabilities=capabilities,
    )


# =============================================================================
# PREPROCESSING ENDPOINTS
# =============================================================================

@router.get("/preprocessing", response_model=List[PreprocessingMethodResponse])
async def list_preprocessing_methods(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    List all preprocessing methods.

    Optionally filter by category (missing_values, scaling, encoding, outliers, cleaning).
    """
    if category:
        methods = get_methods_by_category(category)
    else:
        methods = get_all_methods()

    return [
        PreprocessingMethodResponse(
            slug=m["slug"],
            name=m["name"],
            description=m["description"],
            category=m["category"],
            appliesTo=m["applies_to"],
            parameters=m["parameters"],
        )
        for m in methods
    ]


@router.get("/preprocessing/categories", response_model=List[PreprocessingCategoryResponse])
async def list_preprocessing_categories():
    """List all preprocessing categories."""
    return [
        PreprocessingCategoryResponse(
            key=c["key"],
            name=c["name"],
            description=c["description"],
            icon=c["icon"],
        )
        for c in PREPROCESSING_CATEGORIES
    ]


@router.get("/preprocessing/{slug}", response_model=PreprocessingMethodResponse)
async def get_preprocessing_method_detail(slug: str):
    """Get detailed information about a preprocessing method."""
    method = get_method(slug)
    if method is None:
        raise HTTPException(status_code=404, detail=f"Preprocessing method not found: {slug}")

    return PreprocessingMethodResponse(
        slug=method["slug"],
        name=method["name"],
        description=method["description"],
        category=method["category"],
        appliesTo=method["applies_to"],
        parameters=method["parameters"],
    )


# =============================================================================
# METRICS & PLOTS ENDPOINTS
# =============================================================================

@router.get("/metrics", response_model=List[MetricDefinitionResponse])
async def list_metrics(
    problem_type: Optional[str] = Query(None, description="Filter by problem type")
):
    """
    List all available evaluation metrics.

    Optionally filter by problem type.
    """
    if problem_type:
        metrics = get_metrics_for_problem_type(problem_type)
    else:
        metrics = list(METRIC_DEFINITIONS.values())

    return [
        MetricDefinitionResponse(
            key=m.key,
            name=m.name,
            description=m.description,
            category=m.category.value,
            higherIsBetter=m.higher_is_better,
            appliesTo=m.applies_to,
            cost=m.cost,
        )
        for m in metrics
    ]


@router.get("/plots", response_model=List[PlotDefinitionResponse])
async def list_plots(
    problem_type: Optional[str] = Query(None, description="Filter by problem type"),
    model_category: Optional[str] = Query(None, description="Filter by model category"),
):
    """
    List all available visualization plots.

    Optionally filter by problem type and/or model category.
    """
    if problem_type:
        plots = get_plots_for_problem_type(problem_type, model_category)
    else:
        plots = list(PLOT_DEFINITIONS.values())

    return [
        PlotDefinitionResponse(
            key=p.key,
            name=p.name,
            description=p.description,
            category=p.category.value,
            appliesTo=p.applies_to,
            modelCategories=p.model_categories,
            cost=p.cost,
        )
        for p in plots
    ]
