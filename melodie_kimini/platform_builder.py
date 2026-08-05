import click
from melodie_kimini.models_catalog import get_all_model_ids, get_model_info

@click.group()
def platform():
    """Melodie-Kimini AI Platform - Unlimited Token Access"""
    pass

@platform.command()
@click.argument('model_id')
def launch(model_id):
    """Launch platform with specified model id"""
    info = get_model_info(model_id)
    if info is None:
        click.echo(f"Unknown model: {model_id}. Use 'platform list' to see all models.")
        return
    click.echo(f"Initializing Melodie-Kimini Platform with model: {model_id} (v{info['version']}, {info['tier']})...")
    click.echo("System Ready. Unlimited Tokens Active.")

@platform.command()
def list_models():
    """List all 56 available models"""
    models = get_all_model_ids()
    click.echo(f"Available Models ({len(models)} total):")
    for model in models:
        info = get_model_info(model)
        click.echo(f"- {model:<30} v{info['version']:<5} {info['tier']:<14} {info['context']:,} ctx")

if __name__ == '__main__':
    platform()
