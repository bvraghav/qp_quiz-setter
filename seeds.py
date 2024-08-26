import random
import click


@click.command(context_settings = dict(
  show_default                  = True,
  help_option_names             = ['-h','--help']
))
@click.option('-n', '--num-sets', type=int, default=1)

def main(num_sets,):
  B = random.randbytes(num_sets * 4)
  print (' '.join(
    f'{int.from_bytes(B[4*i:4*(i+1)]):08x}'
    for i in range(num_sets)
  ))

if __name__ == '__main__' :
  main()
