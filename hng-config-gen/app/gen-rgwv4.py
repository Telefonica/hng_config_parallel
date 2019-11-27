# 
# Title: CCN Rural Gateway Configuration Generator program
# Author: Jose Núñez <jose.nunezmartinez@telefonica.com>
# Description: a program to generate the commands necessary to rule Rural Gateway concatenation
#
# Based on jinja2 templates and yml file the Rural Gateway configuraiton commands can be genereated. 
#
#!/usr/bin/env python3


import click
import sys

from pathlib import Path
from src.scripter import *

@click.command()
@click.option('--src', '-i', type=click.File('r'), help='The YAML file.')
@click.option('--dest', '-o', type=str, help='The name of the generated script file.')
@click.option('--override/--no-override', default=True, help='Deletes the old file if it is overwritten.')
@click.option('--comments/--no-comments', default=True, help='Deletes comments in the generated script.')
@click.option('--headers/--no-headers', default=True, help='Deletes headers in the generated script.')
@click.option('--verbose', '-v', is_flag=True, help='Outputs the final script to the console.')
@click.pass_context
@click.version_option('1.2.9', '--version')
def cli(ctx, src, dest, override, comments, headers, verbose):
    """Generates Cisco scripts based on YAML files

    \b
    Examples:
      python gen-rgw.py -i examples/hng.yml
      python gen-rgw.py -i examples/hng.yml -o r1.txt
      python gen-rgw.py -i examples/hng.yml -o r1.txt -v
      python gen-rgw.py -i examples/hng.yml -o r1.txt --no-comments -v
      python gen-rgw.py -i examples/hng.yml -o r1.txt --no-comments --no-headers -v
      python gen-rgw.py -i examples/hng.yml -o r1.txt --no-override

    """
    if src:
        if not dest:
            if '/' in src.name:
                dest = src.name.split('/')[1].split('.')[0] + '.txt'
            else:
                dest = src.name.split('.')[0] + '.txt'

        if not override and Path(dest).is_file():
            print("Error: Existing file ({})".format(dest))
            sys.exit(1)
        if 'hngv4' in src.name:
            Scripter(src.name, dest, 'hngv4', comments, headers).run(verbose) #Full config for rel 4
        elif 'hngv3' in src.name:
            Scripter(src.name, dest, 'hng', comments, headers).run(verbose) #Full config for rel 3
        elif 'test' in src.name:
            Scripter(src.name, dest, 'hng', comments, headers).run(verbose) #Test some feature
        else:
            print("Error: Invalid YAML file ({})".format(src.name))
            sys.exit(1)
    else:
        click.echo(ctx.get_help())

cli()
