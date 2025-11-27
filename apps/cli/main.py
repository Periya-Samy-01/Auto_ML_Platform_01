# cli/main.py
"""
CLI entry point for trainer and preprocessor testing.
Handles command parsing and execution.
Supports supervised (classification, regression) and unsupervised (clustering, dimensionality_reduction) tasks.
"""

import click
import json
from cli.commands.train import train_command
from cli.commands.preprocess import preprocess_command
from cli.utils.trainer_factory import list_available_algorithms
from cli.utils.preprocessor_factory import (
    list_available_preprocessors,
    get_preprocessor_info,
    PREPROCESSOR_DESCRIPTIONS
)


@click.group()
def cli():
    """
    AutoML Platform CLI - Test trainers and preprocessors
    
    Supports:
    - Training: classification, regression, clustering, dimensionality_reduction
    - Preprocessing: missing values, outliers, scaling, encoding, etc.
    """
    pass


# =============================================================================
# TRAIN COMMAND
# =============================================================================

@cli.command()
@click.option(
    '--algorithm',
    required=True,
    help='Algorithm to train (e.g., decision_tree, kmeans, pca)',
    type=str
)
@click.option(
    '--task',
    required=True,
    help='Task type',
    type=click.Choice(['classification', 'regression', 'clustering', 'dimensionality_reduction'], case_sensitive=False)
)
@click.option(
    '--dataset',
    required=True,
    help='Path to CSV dataset',
    type=click.Path(exists=True)
)
@click.option(
    '--target',
    required=False,
    default=None,
    help='Target column name (required for supervised: classification, regression)',
    type=str
)
@click.option(
    '--use-full-dataset',
    is_flag=True,
    default=False,
    help='Use full dataset without train/test split (default: 80/20 split)'
)
@click.option(
    '--n-components',
    required=False,
    default=None,
    type=int,
    help='Number of components (for PCA only)'
)
def train(algorithm: str, task: str, dataset: str, target: str, use_full_dataset: bool, n_components: int):
    """
    Train a model on the provided dataset.
    
    Examples:
    
    \b
    Classification (supervised):
        python -m cli.main train \\
            --algorithm decision_tree \\
            --task classification \\
            --dataset cli/datasets/wine.csv \\
            --target target
    
    \b
    Clustering (unsupervised, full dataset):
        python -m cli.main train \\
            --algorithm kmeans \\
            --task clustering \\
            --dataset cli/datasets/wine.csv \\
            --use-full-dataset
    
    \b
    Dimensionality Reduction (unsupervised, full dataset, 2 components):
        python -m cli.main train \\
            --algorithm pca \\
            --task dimensionality_reduction \\
            --dataset cli/datasets/wine.csv \\
            --n-components 2 \\
            --use-full-dataset
    """
    try:
        # Normalize task
        task = task.lower()
        
        # Validate task-specific requirements
        supervised_tasks = {'classification', 'regression'}
        unsupervised_tasks = {'clustering', 'dimensionality_reduction'}
        
        if task in supervised_tasks and target is None:
            raise click.ClickException(
                f"Task '{task}' requires --target column. "
                f"Example: --target target_column"
            )
        
        if task in unsupervised_tasks and target is not None:
            click.echo(f"⚠️  Warning: --target ignored for unsupervised task '{task}'")
        
        if task == 'dimensionality_reduction' and n_components is None:
            click.echo("⚠️  Warning: --n-components not specified for PCA. Using default (2)")
        
        # Call train command
        train_command(
            algorithm=algorithm,
            task=task,
            dataset=dataset,
            target=target,
            use_full_dataset=use_full_dataset,
            n_components=n_components
        )
        
    except Exception as e:
        # Click will handle the exit
        raise click.ClickException(str(e))


# =============================================================================
# PREPROCESS COMMAND
# =============================================================================

@cli.command()
@click.option(
    '--method',
    required=True,
    help='Preprocessing method (e.g., missing_value_imputation, outlier_handling, feature_scaling)',
    type=str
)
@click.option(
    '--dataset',
    required=True,
    help='Path to input CSV dataset',
    type=click.Path(exists=True)
)
@click.option(
    '--output',
    required=True,
    help='Output path for processed CSV (without extension)',
    type=str
)
@click.option(
    '--target',
    required=False,
    default=None,
    help='Target column name (preserved in output, not modified)',
    type=str
)
@click.option(
    '--params',
    required=False,
    default=None,
    help='JSON string of preprocessor parameters (e.g., \'{"strategy": "mean"}\')',
    type=str
)
def preprocess(method: str, dataset: str, output: str, target: str, params: str):
    """
    Apply preprocessing to a dataset.
    
    Examples:
    
    \b
    Remove duplicates:
        python -m cli.main preprocess \\
            --method duplicate_removal \\
            --dataset cli/datasets/data.csv \\
            --output cli/outputs/cleaned
    
    \b
    Handle missing values (mean imputation):
        python -m cli.main preprocess \\
            --method missing_value_imputation \\
            --dataset cli/datasets/data.csv \\
            --output cli/outputs/imputed \\
            --params '{"strategy": "mean"}'
    
    \b
    Handle outliers (IQR method, clip):
        python -m cli.main preprocess \\
            --method outlier_handling \\
            --dataset cli/datasets/data.csv \\
            --output cli/outputs/no_outliers \\
            --params '{"method": "iqr", "action": "clip", "threshold": 1.5}'
    
    \b
    Feature scaling (standard scaler):
        python -m cli.main preprocess \\
            --method feature_scaling \\
            --dataset cli/datasets/data.csv \\
            --output cli/outputs/scaled \\
            --params '{"method": "standard"}'
    
    \b
    One-hot encoding:
        python -m cli.main preprocess \\
            --method one_hot_encoding \\
            --dataset cli/datasets/data.csv \\
            --output cli/outputs/encoded \\
            --target target_column \\
            --params '{"columns": ["category_col"], "drop_first": true}'
    
    \b
    Label encoding:
        python -m cli.main preprocess \\
            --method ordinal_label_encoding \\
            --dataset cli/datasets/data.csv \\
            --output cli/outputs/label_encoded \\
            --params '{"mode": "label"}'
    
    \b
    Datetime feature extraction:
        python -m cli.main preprocess \\
            --method datetime_feature_extraction \\
            --dataset cli/datasets/data.csv \\
            --output cli/outputs/datetime_features \\
            --params '{"features": ["year", "month", "day", "weekday", "is_weekend"]}'
    """
    try:
        # Parse params JSON if provided
        parsed_params = None
        if params:
            try:
                parsed_params = json.loads(params)
            except json.JSONDecodeError as e:
                raise click.ClickException(
                    f"Invalid JSON in --params: {str(e)}\n"
                    f"Example: --params '{{\"strategy\": \"mean\"}}'"
                )
        
        # Call preprocess command
        preprocess_command(
            method=method,
            dataset=dataset,
            output=output,
            target=target,
            params=parsed_params
        )
        
    except Exception as e:
        raise click.ClickException(str(e))


# =============================================================================
# LIST COMMANDS
# =============================================================================

@cli.command()
@click.option(
    '--task-type',
    required=False,
    type=click.Choice(['supervised', 'unsupervised', 'all'], case_sensitive=False),
    default='all',
    help='Filter by task type'
)
def list_algorithms(task_type: str):
    """
    List all available training algorithms.
    
    Examples:
    
    \b
    All algorithms:
        python -m cli.main list-algorithms
    
    \b
    Only supervised:
        python -m cli.main list-algorithms --task-type supervised
    
    \b
    Only unsupervised:
        python -m cli.main list-algorithms --task-type unsupervised
    """
    task_type = task_type.lower()
    
    if task_type == 'all':
        algorithms = list_available_algorithms()
        click.echo("📊 All available algorithms:")
    elif task_type == 'supervised':
        algorithms = list_available_algorithms(task_type='supervised')
        click.echo("📊 Supervised algorithms (classification, regression):")
    elif task_type == 'unsupervised':
        algorithms = list_available_algorithms(task_type='unsupervised')
        click.echo("📊 Unsupervised algorithms (clustering, dimensionality_reduction):")
    
    for algo in algorithms:
        click.echo(f"  ✓ {algo}")


@cli.command()
@click.option(
    '--verbose',
    is_flag=True,
    default=False,
    help='Show detailed descriptions'
)
def list_preprocessors(verbose: bool):
    """
    List all available preprocessing methods.
    
    Examples:
    
    \b
    List all preprocessors:
        python -m cli.main list-preprocessors
    
    \b
    With descriptions:
        python -m cli.main list-preprocessors --verbose
    """
    preprocessors = list_available_preprocessors()
    click.echo("🔧 Available preprocessing methods:\n")
    
    for name in preprocessors:
        if verbose:
            description = PREPROCESSOR_DESCRIPTIONS.get(name, "")
            click.echo(f"  ✓ {name}")
            click.echo(f"    {description}\n")
        else:
            click.echo(f"  ✓ {name}")
    
    click.echo("\nUse --verbose for descriptions")
    click.echo("Use 'preprocess --method <name> --help' for parameter details")


@cli.command()
@click.argument('method', required=True)
def preprocessor_info(method: str):
    """
    Show detailed information about a preprocessor.
    
    Examples:
    
    \b
        python -m cli.main preprocessor-info missing_value_imputation
        python -m cli.main preprocessor-info outlier_handling
    """
    try:
        info = get_preprocessor_info(method)
        
        click.echo(f"\n📋 Preprocessor: {info['name']}")
        click.echo(f"   Class: {info['class']}")
        click.echo(f"   Description: {info['description']}")
        
        if info['aliases']:
            click.echo(f"   Aliases: {', '.join(info['aliases'])}")
        
        click.echo("")
        
    except ValueError as e:
        raise click.ClickException(str(e))


if __name__ == '__main__':
    cli()
