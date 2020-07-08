import boto3
import click
import math
import os
from pathlib import Path



DEIDENT_UNIT_COST = 0.0014
DEIDENT_UNIT_SIZE = 100
DEFAULT_REGION = 'us-west-2'

client = boto3.client("comprehendmedical", region=DEFAULT_REGION)


def scrub_text(text):
    """Returns text with all PHI removed and replaced with category tags."""
    if len(text) < 1:
        return ""
    response = client.detect_phi(Text=text)
    offsets = []
    for offset in response["Entities"]:
        offsets.append(offset)
    for offset in reversed(offsets):
        text = text[: offset["BeginOffset"]] + "[" + offset["Type"] + "]" + text[offset["EndOffset"] :]
    return text


def get_cost_estimate(text):
    """Estimates the cost of deidentifying a blob of text"""
    if len(text) <= 0:
        return 0
    return math.ceil(len(text) / DEIDENT_UNIT_SIZE) * DEIDENT_UNIT_COST


def scrub_directory(directory, saveto=False):
    """Recursively scrubs the entire directory."""
    if not saveto:
        saveto = directory
    directory = Path(directory)
    saveto = Path(saveto)
    for filename in os.listdir(directory):
        filepath = directory / filename
        scrubbedfilepath = saveto / filename
        if filepath.is_dir():
            if not scrubbedfilepath.exists():
                os.mkdir(scrubbedfilepath)
            scrub_directory(filepath, scrubbedfilepath)
        else:
            scrubbedfilepath.write_text(scrub_text(filepath.read_text()))


def scrub_directory_cost(directory):
    """Estimates the cost of deidentifying a full directory"""
    cost = 0
    directory = Path(directory)
    for filename in os.listdir(directory):
        filepath = directory / filename
        if filepath.is_dir():
            cost += scrub_directory_cost(filepath)
        else:
            cost += get_cost_estimate(filepath.read_text())
    return cost


@click.group()
@click.pass_context
def cli(ctx):
    """Makes it so the default CLICK action is to return the help menu."""
    if ctx.parent:
        print(ctx.parent.get_help())


@cli.command(short_help="Scrub a file.")
@click.argument("input", type=click.File("rb"))
@click.argument("output", type=click.File("wb"))
def scrub(input, output):
    """Scrubs a single file and outputs it where told."""
    output.write(scrub_text(input.read().decode()).encode())


@cli.command(short_help="Estimate cost to scrub a file.")
@click.argument("input", type=click.File("rb"))
def estimate_cost(input):
    """Estimates the cost to scrub a single file."""
    click.echo(get_cost_estimate(input.read()))


@cli.command(short_help="Scrub all the files in a directory recursively.")
@click.argument("input", type=click.Path(exists=True, file_okay=False, resolve_path=True))
@click.argument("output", type=click.Path(exists=True, file_okay=False, resolve_path=True))
def scrub_dir(input, output):
    """Scrubs a directory and outputs the results where told."""
    scrub_directory(input, output)


@cli.command(short_help="Estimate cost to scrub a file.")
@click.argument("input", type=click.Path(exists=True, file_okay=False, resolve_path=True))
def estimate_directory_cost(input):
    """Estimates the cost to scrub a full directory."""
    click.echo(scrub_directory_cost(input))


if __name__ == "__main__":
    cli()
