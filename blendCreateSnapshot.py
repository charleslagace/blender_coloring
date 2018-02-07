#!/usr/bin/env python

import numpy as np
import os
import glob
import csv #07/02/2018
from argparse import ArgumentParser #05/02/2018

if __name__ == "__main__":
    parser = ArgumentParser(description="""A powerful tool for visualizing your brain data with Blender.
                                        Our implementation currently supports nothing.""")  
    
    subparsers = parser.add_subparsers(help="Method of data collection", dest="input_type")
    
    discrete = subparsers.add_parser("discrete", help="""Brain subdivided into discrete regions. For this method,
                                     we expect data matrices in .csv files where each row is a label, and each 
                                     column is an individual measurement. The labels are specified by the Blender
                                     models and the label mapping in your JSON file. Please note that your data 
                                     entries should be quantifiable.""")
    discrete.add_argument("-m", "--models", type=str, help="Directory which contains the Blender models")
    discrete.add_argument("-l", "--labels", type=str, help="JSON file with mapping from atlases to labels")
    discrete.add_argument("-d", "--data", type=str, help="directory with data matrices")
    discrete.add_argument("-a", "--add", action="append", choices=["latex", "animation"], default=[],
                          help="""latex: create a LaTeX file with 1 figure per data matrix\n
                          animation: create a 2D animation from each matrix""")
    
    opt = parser.parse_args()

    if opt.input_type == "discrete":
    
        EXPERIMENT_NAME = opt.data
            
        INPUT_FILES_LONG = np.sort(glob.glob("%s/*.csv" % EXPERIMENT_NAME))
        INPUT_FILES_SHORT = [x.split("/")[-1][:-4] for x in INPUT_FILES_LONG]
        print(INPUT_FILES_SHORT)
        
        OUT_FOLDER = 'output/%s' % EXPERIMENT_NAME
        
#currently here 07/02/2018

#OUT_FOLDERS = [ 'output/%s' for x in MAT_NAMES] # output folders, one per matrix
NR_SIGN_LEVELS = 3 # number of significance levels
# white -> yellow -> orange -> red
#COLOR_POINTS = [np.array(x) for x in [(1,1,1), (1,1,0), (1,0.64,0), (1, 0, 0)]]
COLOR_POINTS = [np.array(x) for x in [(1,1,1), (1,0,0), (1,0,1), (0, 0, 1)]]
corticalEnvVar = os.getenv('cortical')
print(corticalEnvVar)
#if args.cortical:
if corticalEnvVar == '1':
  IMG_TYPE = 'cortical'
else:
  IMG_TYPE = 'subcortical'
#BRAIN_TYPE = 'inflated'
BRAIN_TYPE = 'pial'

#print(SNAP_STAGES, NR_STAGES, labels, nonZlabels)

# take the EBMlabels and find their indices, then construct the two indexMaps below
# 'Frontal Lobe Atrophy' 0
# 'Parietal Lobe Atrophy' 1
# 'Temporal Lobe Atrophy' 2
# 'Occipital Lobe Atrophy' ...
# 'Cingulate Atrophy'
# 'Insula Atrophy'
# 'Amygdala Atrophy'
# 'Hippocampus Atrophy'
# 'Pallidum Atrophy'
# 'Putamen Atrophy'
# 'Thalamus Atrophy'

# map to amygdala 6, hippocampus 7, pallidum 8, putamen 9, thalamus 10
subcortAreasIndexMap = {'Left-Accumbens-area':-1, 'Left-Caudate':-1,
  'Left-Cerebellum-White-Matter':-1, 'Left-Inf-Lat-Vent':-1,
  'Left-Pallidum':8, 'Left-Thalamus-Proper':10, 'Left-Amygdala':6,
  'Left-Cerebellum-Cortex':-1, 'Left-Hippocampus':7, 'Left-Lateral-Ventricle':-1,
  'Left-Putamen':9, 'Left-VentralDC':-1}
# map between subcortical areas and the biomarkers from EBMlabels, used in Alex's matrices, starting from 0
subcortRightAreas = ['Right' + x[4:] for x in subcortAreasIndexMap.keys()]
subcortRightAreasIndexMap = dict(zip(subcortRightAreas, subcortAreasIndexMap.values()))
subcortAreasIndexMap.update(subcortRightAreasIndexMap)
subcortAreas = [x for x in subcortAreasIndexMap.keys() if subcortAreasIndexMap[x] != -1]
subcortFiles = ['./models/subcortical_ply/%s.ply' % x for x in subcortAreas]
#subcortAreasIndexMap = [12, 9, 6, -1, 11, 13, 8, 6, 7, -1, 10, -1]

# map to frontal 0, parietal 1, temporal 2, occipital 3, cingulate 4, insula 5
cortAreasIndexMap = {'bankssts':-1, 'caudalanteriorcingulate':4,
  'caudalmiddlefrontal':0, 'cuneus':3, 'entorhinal':2, 'frontalpole':0,
  'fusiform':2, 'inferiorparietal':1, 'inferiortemporal':2, 'insula':5,
  'isthmuscingulate':4, 'lateraloccipital':3, 'lateralorbitofrontal':0,
  'lingual':3, 'medialorbitofrontal':0, 'middletemporal':2, 'paracentral':0,
  'parahippocampal':2, 'parsopercularis':0, 'parsorbitalis':0,
  'parstriangularis':0, 'pericalcarine':3, 'postcentral':1,
  'posteriorcingulate':4, 'precentral':0, 'precuneus':1,
  'rostralanteriorcingulate':4, 'rostralmiddlefrontal':0,
  'superiorfrontal':0, 'superiorparietal':1, 'superiortemporal':2,
  'supramarginal':1, 'temporalpole':2, 'transversetemporal':2, 'unknown':-1}
cortAreas = cortAreasIndexMap.keys()

cortFilesRight = ['models/DK_atlas_%s/rh.%s.DK.%s.ply' % (BRAIN_TYPE, BRAIN_TYPE, x) for x in cortAreas]
cortFilesLeft = ['models/DK_atlas_%s/lh.%s.DK.%s.ply' % (BRAIN_TYPE, BRAIN_TYPE, x) for x in cortAreas]
cortFilesAll = cortFilesLeft + cortFilesRight
cortAreasNamesFull = [x.split("/")[-1][:-4] for x in cortFilesAll]
#make cortAreasIndexMap map from blender obj name to index of biomk in nonZlabels
cortAreasIndexMap = dict(zip(cortAreasNamesFull, 2*list(cortAreasIndexMap.values())))

blobsNames = []
blobsLabels = []
blobsNonZNrs = []
NR_BALLS = len(blobsNonZNrs)
assert len(blobsNonZNrs) == len(blobsLabels) == len(blobsNames)
BALL_COORDS = [(-1.6,-3.4), (-0.7,-3.4), (0.2,-3.4), (-1.6,-4.2), (-0.7,-4.2), (0.2,-4.2)]

# merge the 2 dicts
#allRegionsIndexMap = subcortAreasIndexMap.copy()
#allRegionsIndexMap.update(cortAreasIndexMap)

nrSubcortRegions = len(subcortAreas)
nrCortRegions = len(cortFilesAll)

if IMG_TYPE == 'subcortical':
  #loadSubcortical(cortFilesRight,subcortFiles)
  painter = SubcorticalPainter(cortFilesRight,subcortFiles)
  indexMap = subcortAreasIndexMap
elif IMG_TYPE == 'cortical':
  #loadCortical(cortFilesAll)
  painter = CorticalPainter(cortFilesAll)
  indexMap = cortAreasIndexMap
else:
  raise ValueError('mode has to be either cortical or subcortical')

painter.prepareScene()
painter.loadMeshes()

testFlag = False

if testFlag:
  fileIndices = [-1]
else:
  fileIndices = range(len(INPUT_FILES_SHORT)) # don't do 'Static', as a different script is used for that

print('fileIndices', fileIndices)

for fileIndex in fileIndices:
  # for ADNI files map to ADNI label order
  indexMapCurr = indexMap.copy()

  """matDict = scipy.io.loadmat(INPUT_FILES_LONG[fileIndex])
  #print(matDict)
  labels = [ x[0] for x in matDict['EBMeventlabels'][0]] # temporal-1 sigma, frontal 1-sigma, temporal-2 sigma, etc ..]
  nonZlabels = [ x[0] for x in matDict['EBMlabels'][0]] # temporal, frontal, etc .."""
  
  with open('temp_csv_files/EBMeventlabels.csv', 'r') as f:
    reader = csv.reader(f)
    labels = [j for i in list(reader) for j in i]
    
  with open('temp_csv_files/EBMlabels.csv', 'r') as f:
    reader = csv.reader(f)
    nonZlabels = [j for i in list(reader) for j in i]
  
  print('-------------%s---------', INPUT_FILES_SHORT[fileIndex])
  print(labels)
  print(nonZlabels)
  nonZtoZMap = createNonZtoZmap(nonZlabels, labels) # list of lists containing the indices where each sigma level-event is in the labels array, grouped by biomk
  #print(nonZlabels, labels, nonZtoZMap)

  """MAT_NAMES = [x for x in matDict.keys() if x.startswith('PVD')]
  MAT_NAMES.sort()
  mats = [matDict[k] for k in MAT_NAMES]"""
  
  MAT_NAMES = glob.glob('temp_csv_files/PVD*')
  print(MAT_NAMES) 
  
  mats = []
  for mat in MAT_NAMES:
    mats.append(np.genfromtxt(mat, delimiter=','))
  
  #zscoreEventIndices = matDict['zscore_event'] # array of numbers showing which sigma level is used in entries of labels
  NR_MATRICES = len(mats)
  print('NR_MATRICES', NR_MATRICES)
  # print(adsa)
  #NR_STAGES = int(len(labels)/5) # number of snapshots to display during the progression
  #SNAP_STAGES = getStages(NR_EVENTS, NR_STAGES) # stages at which to take the snapshots
  NR_EVENTS = len(labels) # nr events, could be more than nr of biomk if different sigma levels are used
  SNAP_STAGES = range(NR_EVENTS+1) # stages at which to take the snapshots
  NR_STAGES = len(SNAP_STAGES)
  
  # generate latex and write it to file
  inputFile = INPUT_FILES_SHORT[fileIndex]
  outFolderCurrMat = '%s/%s' % (OUT_FOLDER, inputFile)
  text = createLatex(NR_MATRICES, NR_STAGES, NR_EVENTS,
  mats, MAT_NAMES, SNAP_STAGES, nonZtoZMap, blobsNonZNrs, blobsNames,
    NR_SIGN_LEVELS, COLOR_POINTS, NR_BALLS, BALL_COORDS, blobsLabels)
  #print(text)
  os.system('mkdir -p %s' % outFolderCurrMat)
  out = open('%s/gen.tex' % outFolderCurrMat, 'w')
  out.write(text)
  out.close()
  #os.system("cd %s && xelatex %s" % (outFileName.split("/")[0], outFileName.split("/")[1] ))
  # os.system("cd %s && pdflatex %s" % (outFileName.split("/")[0], outFileName.split("/")[1] ))

  # print(adas)
  colorRegionsAndRender(indexMapCurr, NR_MATRICES, NR_STAGES, NR_EVENTS,
  mats, MAT_NAMES, SNAP_STAGES, nonZtoZMap, NR_SIGN_LEVELS, COLOR_POINTS, OUT_FOLDER, inputFile, IMG_TYPE)

#print(asda)

#delobj()
