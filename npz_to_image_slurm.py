import numpy as np
import pandas as pd
from math import sqrt
import matplotlib.pyplot as plt
import os
import argparse
import multiprocessing as mul

def to_image(event, mask, map):
  """ Recibe Dataframe de evento (id, charge, time) y retorna una matriz de la imagen"""
  # Se crea una matriz del tamaño del tanque desenrollado (mismo tamaño que máscara)
  # pero con dos canales: (corriente, tiempo de activación)
  event_image = np.zeros(mask.shape + (2,))

  # Se itera sobre cada pmt activado en el evento
  for index, pmt in event.iterrows():
    id = pmt['id']
    charge = pmt['charge']
    time = pmt['time']

    # Si el pmt activado no está en la tapa, se actualizan los valores
    if id in map:
      (i_mask, j_mask) = map[id]
      event_image[i_mask][j_mask] = np.array([charge, time])

  return event_image


def npz_to_images(npz, mask, filename, debug):
    data = npz

    if data['pid'][0] == 11:
        print('Processing e-')
    elif data['pid'][0] == 13:
        print('Processing mu-')
    elif data['pid'][0] == 22:
        print('Processing gamma')

    # Primero se preprocesa la máscara para hacerla de acceso aleatorio con llave valor
    # Llave (PMT_id) -> Valor ((x, y) en máscara)

    map = {  }

    for i in range(len(mask)):
      for j in range(len(mask[i])):
        pmt_id = mask[i][j]
        map[pmt_id] = (i, j)

    images = []

    for i in data['event_id']:

      event = {
        'id': data['digi_hit_pmt'][i],
        'charge': data['digi_hit_charge'][i],
        'time': data['digi_hit_time'][i],
      }

      event = pd.DataFrame(event)
      images.append(to_image(event, mask, map))

    images = np.array(images)
    if debug:
        plt.imshow(images[0, :, :, 0])
        plt.show()

    output = os.path.basename(filename).split('.')[0]
    output = 'IMAGES_' + output
    print(f'{len(images)} processed in {filename} stored in {output}.npy')
    np.save(output, images)

    return images



def is_valid_file(parser, arg, extension):
    if not arg.endswith(extension):
        parser.error(f"The file provided is not {extension}")
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    return arg

def dir_path(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def process_file(filename, args, mask, dbg):
    if filename.endswith(".npz"):
        path = os.path.join(args.dir, filename)
        data = np.load(path, allow_pickle=True)
        npz_to_images(data, mask, path, dbg)
        print(f"processing {filename}")
    else:
        print(f"filename {filename} not a .npz")

def main():
    parser = argparse.ArgumentParser(description='Convert .npz event or events to images of the barrel using the same .npy mask')
    parser.add_argument('-m', '--mask', type=lambda x: is_valid_file(parser, x, 'npy'), required=True, help='Path of .npy mask file', metavar="FILE")
    parser.add_argument('-f', '--file', type=lambda x: is_valid_file(parser, x, 'npz'), help='Path to single .npz file')
    parser.add_argument('-d', '--dir', type=dir_path, help='Path to directory with multiple .npz files')
    parser.add_argument('-D', '--debug', type=str, help='set True for plotting an image after processing a simulation')
    args = parser.parse_args()
    debug = args.debug == 'True'

    # Se carga la máscara generada con el otro script, que sirve para identificar la posición de los PMTs en la imagen.
    mask = np.load(args.mask)

    if(args.file is not None):
        print(f'PROCESSING {args.file}')
        # Unico .npz
        data = np.load(args.file, allow_pickle=True)
        npz_to_images(data, mask, args.file, debug)

    elif(args.dir is not None):
        # Múltiples .npz en un directorio
        print(f'PROCESSING ALL FILES INSIDE {args.dir}')
        list_of_filenames = os.listdir(args.dir)
        threads = mul.Pool(5)
        output = threads.starmap(process_file,[(filenames, args, mask, debug) for filenames in list_of_filenames])
    else:
        parser.error('Neither single file or directory provided.')



if __name__ == '__main__':
    main()
