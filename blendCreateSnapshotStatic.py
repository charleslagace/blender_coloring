#!BPY

# import Blender
import scipy.io
import bpy
import numpy as np
import colorsys
from abc import ABC, abstractmethod
import os
import argparse
import sys
import glob
import math

blendFullPath = os.path.abspath('.')
# print(blendFullPath)
os.chdir(blendFullPath)
sys.path.append(blendFullPath)
from blendHelper import *


# filename = 'blendCreateSnapshot10Nov.py'
# exec(compile(open('blendCreateSnapshot10Nov.py').read(), 'blendCreateSnapshot10Nov.py', 'exec'))

# argv = sys.argv

# if "--" not in argv:
#  argv = []  # as if no args are passed
# else:
#  argv = argv[argv.index("--") + 1:]  # get all args after "--"

# parser = argparse.ArgumentParser(description='Launches processes that previously failed, i.e. which have missing idealLiks files')
# parser.add_argument('--cortical', action="store_true", help='set this is you want to draw cortical regions, otherwise will draw subcortical regions')
# args = parser.parse_args()


def colorRegionsAndRender(indexMap, NR_MATRICES, NR_STAGES, NR_EVENTS,
  mats, MAT_NAMES, SNAP_STAGES, nonZtoZMap, NR_SIGN_LEVELS, COLOR_POINTS, OUT_FOLDER, inputFile, IMG_TYPE):
  objList = bpy.context.selected_objects[::-1]  # make sure to remove the cube from the scene
  # print(objList)

  eventsAbnormalityAll = np.zeros([NR_MATRICES, NR_STAGES, NR_EVENTS], float)
  # for matrixIndex in [0]:
  for matrixIndex in range(0, NR_MATRICES):
    # matrixIndex = 0
    matrix = mats[matrixIndex]
    matrixName = MAT_NAMES[matrixIndex]

    for stageIndex in range(NR_STAGES):
      # stageIndex = 3

      # for each event get the sum of all the probabilities until the current stage
      eventsAbnormality = np.sum(matrix[:, :SNAP_STAGES[stageIndex]], 1)

      assert (len(eventsAbnormality) == NR_EVENTS)
      eventsAbnormalityAll[matrixIndex, stageIndex, :] = eventsAbnormality

      # calc abnorm for plottable biomk
      if bpy.context.selected_objects:
        for obj in bpy.context.selected_objects:
          # print(obj.name, obj, obj.type)
          regionName = obj.name

          if regionName in indexMap.keys():
            # 'Left-Caudate -> nonZlabelNr -> [z-labelNrs], between 1-3'
            nonZlabelNr = indexMap[regionName]
            if nonZlabelNr != -1:

              signifAbnorm = eventsAbnormality[nonZlabelNr]
              print("nonZlabelNr", nonZlabelNr, signifAbnorm)

              finalColor = getInterpColor(signifAbnorm - math.floor(signifAbnorm), math.floor(signifAbnorm) + 1,
                NR_SIGN_LEVELS, COLOR_POINTS)
              # print(finalColor)

              # material = makeMaterial('mat_%d_%d_%s' % (matrixIndex, stageIndex, regionName), finalColor, (1,1,1), 1)
              # setMaterial(obj, material)
              # obj.material_slots[0].material = bpy.data.materials['mat_%d_%d_%s' % (matrixIndex, stageIndex, regionName)]
              bpy.data.materials['mat_%s' % regionName].diffuse_color = finalColor

              # obj.data.materials.append(material)

          else:
            print('object not found: %s', obj.name)

      outputFile = '%s/%s/%s/%s_stage%d.png' % (
      OUT_FOLDER, INPUT_FILES_SHORT[fileIndex], matrixName, IMG_TYPE, SNAP_STAGES[stageIndex])
      print('rendering file %s', outputFile)
      bpy.data.scenes['Scene'].render.filepath = outputFile
      bpy.ops.render.render(write_still=True)

  return eventsAbnormalityAll

def createLatex(NR_MATRICES, NR_STAGES, NR_EVENTS,
  mats, MAT_NAMES, SNAP_STAGES, nonZtoZMap, blobsNonZNrs, blobsNames,
    NR_SIGN_LEVELS, COLOR_POINTS, NR_BALLS, BALL_COORDS, blobsLabels):
  eventsAbnormalityAll = np.zeros([NR_MATRICES, NR_STAGES, NR_EVENTS], float)
  text = r'''
\documentclass[11pt,a4paper,oneside]{report}

\usepackage{float}
\usepackage{tikz}
\usetikzlibrary{plotmarks}
\usepackage{amsmath,graphicx}
\usepackage{epstopdf}
\usepackage[font=normal,labelfont=bf]{caption}
\usepackage{subcaption}
\usepackage{color}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{scalefnt}

% margin size
\usepackage[margin=1in]{geometry}

\begin{document}
\belowdisplayskip=12pt plus 3pt minus 9pt
\belowdisplayshortskip=7pt plus 3pt minus 4pt

% scale parameter for the circles and the gradient
\tikzset{every picture/.append style={scale=0.5}}
% scale parameter for the upper and lower small brain images
\newcommand*{\scaleBrainImg}{0.1}'''

  for matrixIndex in range(NR_MATRICES):
    matrix = mats[matrixIndex]

    for stageIndex in range(NR_STAGES):
      # for each event get the sum of all the probabilities until the current stage
      eventsAbnormality = np.sum(matrix[:, :SNAP_STAGES[stageIndex]], 1)

      print(matrix, matrix.shape)
      print(matrix[:, :SNAP_STAGES[stageIndex]])
      print(eventsAbnormality.shape)
      assert (eventsAbnormality.shape[0] == NR_EVENTS)
      eventsAbnormalityAll[matrixIndex, stageIndex, :] = eventsAbnormality

      for ballIndex, blobNZNr in enumerate(blobsNonZNrs):
        #indicesZ = nonZtoZMap[blobNZNr]
        # abnormality values for each significance levels
        signifAbnorm = eventsAbnormality[blobNZNr]
        print("blobName", blobsNames[ballIndex], blobNZNr, signifAbnorm)
        print('nonZtoZMap', nonZtoZMap)

        finalColor = getInterpColor(signifAbnorm - math.floor(signifAbnorm), math.floor(signifAbnorm) + 1,
          NR_SIGN_LEVELS, COLOR_POINTS)
        # print(finalColor)

        text += r'''
\definecolor{col''' + "%d%d%d" % (
          matrixIndex, stageIndex, ballIndex) + '''}{rgb}{''' + '%.3f,%.3f,%.3f' % (
        finalColor[0], finalColor[1], finalColor[2]) + '''}'''

  text += '''\n\n '''

  for matrixIndex in range(NR_MATRICES):
    matrix = mats[matrixIndex]

    text += r'''

\begin{figure}[H]
  \centering'''
    for stageIndex in range(NR_STAGES):

      # for each event get the sum of all the probabilities until the current stage
      eventsAbnormality = np.sum(matrix[:, :SNAP_STAGES[stageIndex]], 1)

      assert (len(eventsAbnormality) == NR_EVENTS)
      eventsAbnormalityAll[matrixIndex, stageIndex, :] = eventsAbnormality

      text += r'''
        %\begin{subfigure}[b]{0.15\textwidth}
      \begin{tikzpicture}[scale=1.0,auto,swap]

      % the two brain figures on top
      \node (cortical_brain) at (0,1.5) { \includegraphics*[scale=\scaleBrainImg,trim=0 0 0 0]{'''

      text += '%s/cortical_stage%d.png' % (MAT_NAMES[matrixIndex], SNAP_STAGES[stageIndex]) + r'''}};
      \node (subcortical_brain) at (0,-1.5) { \includegraphics*[scale=\scaleBrainImg,trim=0 0 0 0]{'''
      text += '%s/subcortical_stage%d.png' % (MAT_NAMES[matrixIndex], SNAP_STAGES[stageIndex]) + r'''}};
      '''
      text += r'''\node (stage) at (0, 3.4) {Stage ''' + "%d" % SNAP_STAGES[stageIndex] + r'''};
      '''

      for ballIndex in range(NR_BALLS):
        text += '''\draw[fill=''' + "col%d%d%d" % (
          matrixIndex, stageIndex, ballIndex) + "] (%1.1f,%1.1f)" % (
        BALL_COORDS[ballIndex][0], BALL_COORDS[ballIndex][1]) + \
                ''' circle [radius=0.33cm] node {\scriptsize ''' + "%s" % blobsLabels[ballIndex] + '''};
          '''

      text += r'''\end{tikzpicture}
    %\end{subfigure}
    % next subfigure
    \hspace{-1.5em}
    ~'''

    upperLimitGradient = 6
    lowerLimitGradient = 0
    chunkLen = ((upperLimitGradient - lowerLimitGradient) / NR_SIGN_LEVELS)
    text += r'''
  \hspace{1em}
  % the red-to-yellow gradient on the right
  \begin{tikzpicture}[scale=1.1,auto,swap]
    \colorlet{redhsb}[hsb]{red}%
    \colorlet{bluehsb}[hsb]{blue}%
    \colorlet{yellowhsb}[hsb]{yellow}%
    \colorlet{orangehsb}[hsb]{orange}%
    \colorlet{magentahsb}[hsb]{magenta}%
    \shade[bottom color=white,top color=red] (0,0) rectangle (0.5,2.01); % bottom rectangle
    \shade[bottom color=red,top color=magenta] (0,2) rectangle (0.5,4.01);
    \shade[bottom color=magenta,top color=blue] (0,4) rectangle (0.5,6); % top rectangle
'''
    sigmaLabels = ['normal', '1-sigma', '2-sigma', '3-sigma']
    for s in range(NR_SIGN_LEVELS + 1):
      text += "\n    \draw (0,%d) -- (0.5,%d);" % (s * chunkLen, s * chunkLen)
      text += r'''\node[inner sep=0] (corr_text) at (1.7,''' + str(s * chunkLen) + r''') {''' + sigmaLabels[s] + r'''};
'''
    text += r'''
  \end{tikzpicture}
  \caption{''' + " ".join(MAT_NAMES[matrixIndex].split("_")) + '''}
\end{figure}
'''

  text += r'''
\end{document}

'''

  return text


EXPERIMENT_NAME = 'alex07Mar2017'
# INPUT_FILES_SHORT = ['14082016', '17082016_ADNI1pt5T', '17082016_ADNI3T', '17082016_C9orf72_1Seq', '17082016_C9orf72', '17082016_GRN', '17082016_MAPT_1Seq', '17082016_MAPT', '17082016_MUTpos']#, '17082016_Static']
# INPUT_FILES_LONG = ['%s/Plotting_Raz_%s.mat' % (EXPERIMENT_NAME, x) for x in INPUT_FILES_SHORT]
INPUT_FILES_LONG = np.sort(glob.glob("%s/*.mat" % EXPERIMENT_NAME))
INPUT_FILES_SHORT = ['_'.join(x.split('_')[3:]).split('.')[0] for x in INPUT_FILES_LONG]
print(INPUT_FILES_SHORT)
OUT_FOLDER = 'output/%s' % EXPERIMENT_NAME

# OUT_FOLDERS = [ 'output/%s' for x in MAT_NAMES] # output folders, one per matrix
NR_SIGN_LEVELS = 3  # number of significance levels
# white -> yellow -> orange -> red
# COLOR_POINTS = [np.array(x) for x in [(1,1,1), (1,1,0), (1,0.64,0), (1, 0, 0)]]
COLOR_POINTS = [np.array(x) for x in [(1, 1, 1), (1, 0, 0), (1, 0, 1), (0, 0, 1)]]
corticalEnvVar = os.getenv('cortical')
print(corticalEnvVar)
# if args.cortical:
if corticalEnvVar == '1':
  IMG_TYPE = 'cortical'
else:
  IMG_TYPE = 'subcortical'
# BRAIN_TYPE = 'inflated'
BRAIN_TYPE = 'pial'

# print(SNAP_STAGES, NR_STAGES, labels, nonZlabels)

subcortAreasIndexMap = {'Left-Accumbens-area': 12, 'Left-Caudate': 9, 'Left-Cerebellum-White-Matter': -1,
                        'Left-Inf-Lat-Vent': -1, 'Left-Pallidum': 11, 'Left-Thalamus-Proper': 13, 'Left-Amygdala': 8,
                        'Left-Cerebellum-Cortex': 6, 'Left-Hippocampus': 7, 'Left-Lateral-Ventricle': -1,
                        'Left-Putamen': 10, 'Left-VentralDC': -1}
# map between subcortical areas and the biomarkers from EBMlabels, used in Alex's matrices, starting from 0
subcortRightAreas = ['Right' + x[4:] for x in subcortAreasIndexMap.keys()]
subcortRightAreasIndexMap = dict(zip(subcortRightAreas, subcortAreasIndexMap.values()))
subcortAreasIndexMap.update(subcortRightAreasIndexMap)
subcortAreas = [x for x in subcortAreasIndexMap.keys() if subcortAreasIndexMap[x] != -1]
subcortFiles = ['./models/subcortical_ply/%s.ply' % x for x in subcortAreas]
# subcortAreasIndexMap = [12, 9, 6, -1, 11, 13, 8, 6, 7, -1, 10, -1]

# map to frontal 0, temporal 1, parietal 2, occipital 3, cingulate 4, insula 5
cortAreasIndexMap = {'bankssts': -1, 'caudalanteriorcingulate': 4, 'caudalmiddlefrontal': 0, 'cuneus': 3,
                     'entorhinal': 1, 'frontalpole': 0, 'fusiform': 1, 'inferiorparietal': 2, 'inferiortemporal': 1,
                     'insula': 5, 'isthmuscingulate': 4, 'lateraloccipital': 3, 'lateralorbitofrontal': 0, 'lingual': 3,
                     'medialorbitofrontal': 0, 'middletemporal': 1, 'paracentral': 0, 'parahippocampal': 1,
                     'parsopercularis': 0, 'parsorbitalis': 0, 'parstriangularis': 0, 'pericalcarine': 3,
                     'postcentral': 2, 'posteriorcingulate': 4, 'precentral': 0, 'precuneus': 2,
                     'rostralanteriorcingulate': 4, 'rostralmiddlefrontal': 0, 'superiorfrontal': 0,
                     'superiorparietal': 2, 'superiortemporal': 1, 'supramarginal': 2, 'temporalpole': 1,
                     'transversetemporal': 1, 'unknown': -1}
cortAreas = cortAreasIndexMap.keys()

cortFilesRight = ['models/DK_atlas_%s/rh.%s.DK.%s.ply' % (BRAIN_TYPE, BRAIN_TYPE, x) for x in cortAreas]
cortFilesLeft = ['models/DK_atlas_%s/lh.%s.DK.%s.ply' % (BRAIN_TYPE, BRAIN_TYPE, x) for x in cortAreas]
cortFilesAll = cortFilesLeft + cortFilesRight
cortAreasNamesFull = [x.split("/")[-1][:-4] for x in cortFilesAll]
# make cortAreasIndexMap map from blender obj name to index of biomk in nonZlabels
cortAreasIndexMap = dict(zip(cortAreasNamesFull, 2 * list(cortAreasIndexMap.values())))

blobsNames = ['Asymmetry']
blobsLabels = ['A']  # asymmetry
blobsNonZNrs = [14]
NR_BALLS = len(blobsNonZNrs)
assert len(blobsNonZNrs) == len(blobsLabels) == len(blobsNames)
BALL_COORDS = [(-1.6, -3.4), (-0.7, -3.4), (0.2, -3.4), (-1.6, -4.2), (-0.7, -4.2), (0.2, -4.2)]

# merge the 2 dicts
# allRegionsIndexMap = subcortAreasIndexMap.copy()
# allRegionsIndexMap.update(cortAreasIndexMap)

nrSubcortRegions = len(subcortAreas)
nrCortRegions = len(cortFilesAll)

if IMG_TYPE == 'subcortical':
  # loadSubcortical(cortFilesRight,subcortFiles)
  painter = SubcorticalPainter(cortFilesRight, subcortFiles)
  indexMap = subcortAreasIndexMap
elif IMG_TYPE == 'cortical':
  # loadCortical(cortFilesAll)
  painter = CorticalPainter(cortFilesAll)
  indexMap = cortAreasIndexMap
else:
  raise ValueError('mode has to be either cortical or subcortical')

painter.prepareScene()
painter.loadMeshes()

fileIndices = [-1] # take the static matrix, usually last in the list.

for fileIndex in fileIndices:
  # for ADNI files map to ADNI label order
  indexMapCurr = indexMap.copy()

  matDict = scipy.io.loadmat(INPUT_FILES_LONG[fileIndex])
  # print(matDict)
  labels = [x[0] for x in matDict['EBMeventlabels'][0]]  # temporal-1 sigma, frontal 1-sigma, temporal-2 sigma, etc ..]
  nonZlabels = [x[0] for x in matDict['EBMlabels'][0]]  # temporal, frontal, etc ..
  print('-------------%s---------', INPUT_FILES_SHORT[fileIndex])
  print(labels)
  print(nonZlabels)
  nonZtoZMap = createNonZtoZmap(nonZlabels,
                                labels)  # list of lists containing the indices where each sigma level-event is in the labels array, grouped by biomk
  # print(nonZlabels, labels, nonZtoZMap)

  MAT_NAMES = [x for x in matDict.keys() if x.startswith('ml_mean_group')]
  MAT_NAMES.sort()
  mats = [matDict[k] for k in MAT_NAMES]
  mats = [np.diag(m).reshape(-1,1) for m in mats]
  assert(mats[0].shape[1] == 1)

  # zscoreEventIndices = matDict['zscore_event'] # array of numbers showing which sigma level is used in entries of labels
  NR_MATRICES = len(mats)
  # NR_STAGES = int(len(labels)/5) # number of snapshots to display during the progression
  # SNAP_STAGES = getStages(NR_EVENTS, NR_STAGES) # stages at which to take the snapshots
  NR_EVENTS = len(nonZlabels)  # nr events, could be more than nr of biomk if different sigma levels are used
  SNAP_STAGES = [1]  # stages at which to take the snapshots
  NR_STAGES = len(SNAP_STAGES)

  # generate latex and write it to file
  inputFile = INPUT_FILES_SHORT[fileIndex]
  outFolderCurrMat = '%s/%s' % (OUT_FOLDER, inputFile)
  text = createLatex(NR_MATRICES, NR_STAGES, NR_EVENTS,
  mats, MAT_NAMES, SNAP_STAGES, nonZtoZMap, blobsNonZNrs, blobsNames,
    NR_SIGN_LEVELS, COLOR_POINTS, NR_BALLS, BALL_COORDS, blobsLabels)
  # print(text)
  os.system('mkdir -p %s' % outFolderCurrMat)
  out = open('%s/gen.tex' % outFolderCurrMat, 'w')
  out.write(text)
  out.close()
  # os.system("cd %s && xelatex %s" % (outFileName.split("/")[0], outFileName.split("/")[1] ))
  # os.system("cd %s && pdflatex %s" % (outFileName.split("/")[0], outFileName.split("/")[1] ))

  colorRegionsAndRender(indexMapCurr, NR_MATRICES, NR_STAGES, NR_EVENTS,
  mats, MAT_NAMES, SNAP_STAGES, nonZtoZMap, NR_SIGN_LEVELS, COLOR_POINTS, OUT_FOLDER, inputFile, IMG_TYPE)

# print(asda)

# delobj()
