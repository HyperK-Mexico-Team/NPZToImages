#!/usr/bin/python3

#SBATCH --output=
#SBATCH --partition=
#SBATCH -n 5


import numpy as np
import pandas as pd
from math import sqrt
import argparse, os
import functools as f


def to_cylindrical(coords):
  x, y, z = coords[0], coords[1], coords[2]
  ro = sqrt(x**2 + y**2)
  theta = np.arctan2(y, x)
  return  ro, theta, z

def most_frequent(lista):
  counter = 0
  num = lista[0]

  for i in lista:
    curr_frequency = lista.count(i)
    if(curr_frequency> counter):
      counter = curr_frequency
      num = i

  return num

def unroll_geometry(geo_file):

  # Se pasan posicion de PMT a coordenadas cilindricas
  keys = list(geo_file.keys())
  if "position" in keys:
    id_pmt = geo_file['tube_no']
    position = geo_file['position']
    height_tank = 1750
  else:
    print("IWCD")
    geom = geo_file["geometry"]
    height_tank = 455
    # geom.shape (d0, d1, d2 . . . dn, p) la dimension P contiene la caracteristica
    # |P| = 6, ya que contiene px,py,pz, ox,oy,oz, la posicion cartesiana y orientacion de
    # cada PMT.

    number_of_pmt = f.reduce(lambda x, y: x*y, geom.shape) // geom.shape[-1]
    id_pmt = [i+1 for i in range(number_of_pmt)]
    position_and_direction = geom.reshape(-1, geom.shape[-1])
    position = position_and_direction[..., :3]

  cyl_coords = np.array([to_cylindrical(coords) for coords in position])

  # Se crea un Dataframe con las posiciones y IDs y se ordena por z y theta
  pmt_pos = {
      'id': id_pmt,
      'theta': cyl_coords[:, 1],
      'z': cyl_coords[:, 2],
  }

  pmt_pos = pd.DataFrame(pmt_pos)

  pmt_pos = pmt_pos.sort_values(by=['z', 'theta'])

  # Quitamos las tapas
  pmt_pos = pmt_pos[abs(pmt_pos['z']) < height_tank]

  # Generacion de la matriz de IDs
  image = [[ int(pmt_pos.iloc[0]['id']) ]]
  current_row = 0
  last_z = pmt_pos.iloc[0]['z']

  # Se recorren los PMTs a lo largo de theta ordenados por z
  for i in range(1, len(pmt_pos)):
    pmt = pmt_pos.iloc[i]
    # Cuando cambia z, significa que estan en la siguiente fila
    if abs(last_z - pmt['z']) > 0.001 :
      image.append([])
      current_row += 1
    last_z = pmt['z']
    image[current_row].append(int(pmt['id']))
  sizes = [len(row) for row in image]
  complete_row = most_frequent(sizes)
  image = [row for row in image if len(row) == complete_row]
  return np.array(image)

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    return arg

def main():
    parser = argparse.ArgumentParser(description='Convert .npz geometry file to .npy matrix where each PMT is a pixel')
    parser.add_argument('-i', type=lambda x: is_valid_file(parser, x), required=True, help='Path of .npz geometry file', metavar="FILE")
    parser.add_argument('-o', type=str, help='Name of .npy output mask', default='mask')
    args = parser.parse_args()

    geo = np.load(args.i, allow_pickle=True)
    image = unroll_geometry(geo)

    print(f"Writing to {args.o}.npy")
    np.save(f'{args.o}.npy', image)


if __name__ == '__main__':
    main()
