import numpy as np
from matplotlib import pyplot as pl


def convert_label_to_array(label_file_path):
    label_file = label_file_path
    label_file_opened = open(label_file, 'r')
    label_lines = label_file_opened.readlines()
    
    vertices_list = []
    for line in label_lines[2:]:
        vertex_number = line.split()[0]
        vertices_list.append(vertex_number)

    return np.array(map(int, vertices_list))

def polygon_maker(mesh_path, label_files, output):
    '''
    Creates a Stanford polygon file http://brainder.org/2011/09/25/braindering-with-ascii-files/
    --------
    mesh_path:  path to freesurfer surface file ([r,l]h.pial or inflated, or sphere)
    label_files: list of labels (absolute paths)
    output = file path for the output ply file (include .ply)
    *assuming there are three files
    '''
    import nibabel as nb
    import matplotlib.pyplot as plt
    import random

    label_files = label_files

    #matplotlib colormaps
    #http://wiki.scipy.org/Cookbook/Matplotlib/Show_colormaps

    mesh = nb.freesurfer.read_geometry(mesh_path)
    vertices = mesh[0]
    faces = mesh[1]

    number_of_vertices = vertices.shape[0]
    number_of_faces = faces.shape[0]
    ply_file = open(output, 'w')
    string = ''
    prefix = '''ply
format ascii 1.0
element vertex {number_of_vertices}
property float x
property float y
property float z
property uchar red
property uchar green
property uchar blue
element face {number_of_faces}
property list uchar int vertex_index
end_header\n'''.format(number_of_vertices = number_of_vertices,
              number_of_faces = number_of_faces)

    for i in range(number_of_vertices):
        current_row = '%f %f %f 255 255 255\n' %( vertices[i][0], vertices[i][1], 
                                           vertices[i][2])
        string = string + current_row

    string = string.split('\n')

    suffix = ''
    #colors = ['9 0 255',
    #          '255 60 0',
    #          '0 255 9']
    nrRegions = len(label_files)
    colors=iter(pl.cm.rainbow(np.linspace(0,1,nrRegions)))


    for i in range(number_of_faces):
        current_row = '3 %d %d %d\n' %(faces[i][0], faces[i][1],
                                       faces[i][2])
        suffix = suffix + current_row

    for number, label in enumerate(label_files):
        label_array = convert_label_to_array(label)
        print label
        color = next(colors) 
        colorStr = ' %d %d %d' % (int(255*color[0]), int(255*color[1]), int(255*color[2]))
        for item in np.nditer(label_array):
            current_row = string[item].split()
            new_row = current_row[0] + ' ' + current_row[1] + ' ' + current_row[2]
            new_row = new_row + colorStr 
            string[item] = new_row
    string = "\n".join(item for item in string)
    string = prefix + string + suffix
    output_file = open(output, 'w')
    output_file.write(string)
    output_file.close()
    return None


def main():
  import sys

  #Frontal Temporal Parietal Occipital Cingulate Insula Cerebellar
  #Hippocampus Amygdala Caudate Putamen Pallidum Accumbens Thalamus

  labelFiles = ['bankssts', 'caudalanteriorcingulate', 'caudalmiddlefrontal', 'corpuscallosum', 'cuneus', 'entorhinal', 'frontalpole', 'fusiform', 'inferiorparietal', 'inferiortemporal', 'insula', 'isthmuscingulate', 'lateraloccipital', 'lateralorbitofrontal', 'lingual', 'medialorbitofrontal', 'middletemporal', 'paracentral', 'parahippocampal', 'parsopercularis', 'parsorbitalis', 'parstriangularis', 'pericalcarine', 'postcentral', 'posteriorcingulate', 'precentral', 'precuneus', 'rostralanteriorcingulate', 'rostralmiddlefrontal', 'superiorfrontal', 'superiorparietal', 'superiortemporal', 'supramarginal', 'temporalpole', 'transversetemporal', 'unknown']

  labelFilesLhFull = ['labels/lh.%s.label' % x for x in labelFiles]

  polygon_maker(mesh_path = 'models/lh.inflated',
                label_files = labelFilesLhFull,
                output = 'output/lh.all.ply' )


if __name__ == "__main__":
    main()

