import numpy as np
import pandas as pd
from math import sqrt
import argparse, os


def to_cylindrical(coords):
  x, y, z = coords[0], coords[1], coords[2]
  ro = sqrt(x**2 + y**2)
  theta = np.arctan2(y, x)
  return  ro, theta, z

def unroll_geometry(geo_file):

  # Se pasan posicion de PMT a coordenadas cilíndricas
  cyl_coords = np.array([to_cylindrical(coords) for coords in geo_file['position']])

  # Se crea un Dataframe con las posiciones y IDs y se ordena por z y theta
  pmt_pos = {
      'id': geo_file['tube_no'],
      'theta': cyl_coords[:, 1],
      'z': geo_file['position'][:,2],
  }
  pmt_pos = pd.DataFrame(pmt_pos)
  pmt_pos = pmt_pos.sort_values(by=['z', 'theta'])

  # Quitamos las tapas
  pmt_pos = pmt_pos[abs(pmt_pos['z']) < 1750]

  # Generación de la matriz de IDs
  image = [[ int(pmt_pos.iloc[0]['id']) ]]
  current_row = 0
  last_z = pmt_pos.iloc[0]['z']

  # Se recorren los PMTs a lo largo de theta ordenados por z
  for i in range(1, len(pmt_pos)):
    pmt = pmt_pos.iloc[i]
    # Cuando cambia z, significa que están en la siguiente fila
    if abs(last_z - pmt['z']) > 0.001 :
      image.append([])
      current_row += 1
    last_z = pmt['z']
    image[current_row].append(int(pmt['id']))

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
