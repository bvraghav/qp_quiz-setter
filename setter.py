import csv
from argparse import Namespace as NS

import random
import click
from pathlib import Path

# -----------------------------------------------------
# Config Defaults
# -----------------------------------------------------
# NUM_SETS = 1
QDB_FNAME = './qdb.csv'
CONTENT_PREFIX_FNAME = 'setter-py--content-prefix.txt'
SETID_PLACEHOLDER = 'CE092FFD_SETID'
Q_PRE = '1. '
Q_SEP = '\n\n\\bvrskipline\n#+attr_latex: :options [resume]\n'
A_PRE = '   1. '
A_SEP = '\n'
QA_SEP = (
  '\\\\\n   #+attr_latex: :environment enumerate* '
  ':options [itemjoin={\quad},]\n'
)
QAMUL_SEP = ''
CONTENT_SUFFIX = '\n\\bvrhrule\n'
# Inferred Config
CONTENT_PREFIX = ''
QDB = []
# -----------------------------------------------------


@click.command(context_settings = dict(
  show_default                  = True,
  help_option_names             = ['-h','--help']
))
@click.option('-s', '--seed')
# @click.option('-n','--num-sets', type=int, default=NUM_SETS)
@click.option('--qdb-path', type=click.Path(
  exists=False, dir_okay=False, path_type=Path,
), default = QDB_FNAME,)
@click.option('--content-prefix-path', type=click.Path(
  exists=False, dir_okay=False, path_type=Path,
), default = CONTENT_PREFIX_FNAME,)
@click.option('--set-id-placeholder',
              default = SETID_PLACEHOLDER,)
@click.option('--q-pre', default=Q_PRE)
@click.option('--q-sep', default=Q_SEP)
@click.option('--a-pre', default=A_PRE)
@click.option('--a-sep', default=A_SEP)
@click.option('--qa-sep', default=QA_SEP)
@click.option('--qa-mul-sep', default=QAMUL_SEP)
@click.option('--content-suffix',
              default=CONTENT_SUFFIX)
def main(
    seed,
    # num_sets,
    qdb_path,
    content_prefix_path,
    set_id_placeholder,
    q_pre,
    q_sep,
    a_pre,
    a_sep,
    qa_sep,
    qa_mul_sep,
    content_suffix,
):
  # Bootstrap
  seed = (int(seed, 16) if seed is not None
          else int.from_bytes(random.randbytes(4)))
  qdb = loadQdb()
  qData = qdb['data']
  qp, key = genQpaperAndKey(qData, seed)
  # fname = fnameFromSeed(seed)

  # with open(fname, 'w') as F :
  #   F.write(qp)

  # print (f'Written to: {fname}')
  # print (f'KEY: {keyAsHumanReadable(key)}')

  print (qp)

def getContentPrefix(
    setId,
    fname = CONTENT_PREFIX_FNAME,
    setIdPlaceholder = SETID_PLACEHOLDER,
):
  global CONTENT_PREFIX

  # Load Content Prefix May Be
  if len(CONTENT_PREFIX) < 1 :
    with open(fname, 'r') as F :
      pref = ''.join(F.readlines())
    
    CONTENT_PREFIX = pref

  # Update Set-ID
  pref = CONTENT_PREFIX
  pref = pref.replace(
    setIdPlaceholder, setId)
  return pref

def loadQdb(fname = QDB_FNAME) :
  qdb = dict()
  with open(fname, 'r', newline='') as F :
    reader = csv.DictReader(F, dialect='excel')
    qdb['header'] = reader.fieldnames
    qdb['data'] = list(reader)
    qdb['numLines'] = len(qdb['data'])

  return qdb

def genQ(Q,A0,A1,A2,A3,A_MUL_P,**_):
  qaSep = (QAMUL_SEP if A_MUL_P else QA_SEP)
  aConcat = A_SEP.join(
    f'{A_PRE}{a}' for a in (A0,A1,A2,A3)
  )
  return f'{Q_PRE}{Q}{qaSep}{aConcat}'

def genQpaperAndKey(qdbData, seed):
  rng = random.Random(seed)
  
  # Randomise Q-Order
  x = qdbData
  qdbData = rng.sample(x, k=len(x))

  # Randomise A-Order and update A
  for q in qdbData :
    oldA = int(q['A'])
    oldAlist = [q['A0'],q['A1'],q['A2'],q['A3']]

    # Randomise so that given shuf[I] = J; the answer
    # new_a[J] <- old_a[I] (NOT the other way round)
    shuf = random.sample(range(4),4)

    # Since I->J (or, J<-I)
    q['A'] = shuf[oldA]
    q[f'A{shuf[0]}'] = oldAlist[0]
    q[f'A{shuf[1]}'] = oldAlist[1]
    q[f'A{shuf[2]}'] = oldAlist[2]
    q[f'A{shuf[3]}'] = oldAlist[3]
    # Type Conversion
    q['A_MUL_P'] = bool(int(q['A_MUL_P']))

  seedHex = f'{seed:08x}'
  prefix = getContentPrefix(seedHex)
  content = Q_SEP.join(genQ(**q) for q in qdbData)
  suffix = CONTENT_SUFFIX
  key = [chr(ord('A')+q['A']) for q in qdbData]
  keyComment = keyAsHumanReadable(key)
  qp = f'{prefix}{content}{suffix}\n\n# {keyComment}'

  return qp, key

def keyAsHumanReadable(aList, groupSize=4):
  s = groupSize
  return ' '.join(
    ''.join(aList[a:b])
   for (a,b) in zip(
       range(0,len(aList),s),
       range(min(s,len(aList)),(s-1)+len(aList),s)
   )
  )

def fnameFromSeed(seed):
  return f'qp-{seed:08x}.org'


if __name__ == '__main__' :

  # loadContentPrefix('Alpha Charlie')

  # print (CONTENT_PREFIX_FNAME)
  # print ()
  # print (CONTENT_PREFIX)
  main()
