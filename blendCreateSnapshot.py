#!BPY

import bpy
import numpy as np
import json #19/03/2018
import os
import sys
import glob
from argparse import ArgumentParser #05/02/2018

blendFullPath = os.path.abspath('.')
os.chdir(blendFullPath)
sys.path.append(blendFullPath)
from blendHelper import *

def main():    
    argv = sys.argv
    
    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"
    
    print(argv)
        
    usageText = ("""A powerful tool for visualizing your brain data with Blender.
                 Our implementation currently supports nothing.""")
    
    parser = ArgumentParser(description=usageText, add_help=False)
    parser.add_argument("-H", "--help_python", action="help", 
                        help="""Show this help message and exit. Note that -h or --help will
                        print the help for Blender.""")    
    
    subparsers = parser.add_subparsers(help="Method of data collection", dest="input_type")
    
    discrete = subparsers.add_parser("discrete", add_help=False,
                                     help="""Brain subdivided into discrete regions. For this method,
                                     we expect data matrices in .csv files where each row is a label,
                                     and each column is an individual measurement. The labels are 
                                     specified by the Blender models and the label mapping in your JSON
                                     file. Please note that your data entries should be quantitative.""")
    discrete.add_argument("-H", "--help_python", action="help", help="show this help message and exit")
    discrete.add_argument("-l", "--labels", type=str, required=True,
                          help="""JSON file with mapping from atlases to labels. 
                          Use -1 for any atlas which should be included in your images.""")
    discrete.add_argument("-d", "--data", type=str, required=True, help="directory with data matrices")
    discrete.add_argument("-a", "--add", action="append", choices=["latex", "animation"], default=[],
                          help="""latex: create a LaTeX file with 1 figure per data matrix\n
                          animation: create a 2D animation from each matrix""") 
    
    opt = parser.parse_args(argv)
    
    if not argv:
        parser.print_help()
        discrete.print_help()
        return

    if opt.input_type == "discrete":
    
        EXPERIMENT_NAME = opt.data
            
        INPUT_FILES_LONG = np.sort(glob.glob("%s/*.csv" % EXPERIMENT_NAME))
        INPUT_FILES_SHORT = [x.split("/")[-1][:-4] for x in INPUT_FILES_LONG]
        print(INPUT_FILES_SHORT)
        
        OUT_FOLDER = 'output/%s' % EXPERIMENT_NAME
        
        with open(opt.labels, 'r') as f:
            indexMap = json.load(f)
            
        print(indexMap)
        
        models = []        

        for mode in indexMap.keys():
            if indexMap[mode]["use"] is True:
                models.append(mode)
        
        if len(models) == 0:
            raise Exception("At least 1 model should be used in the JSON file.")
            
        print("Models used: ", models)
            
        for mode in models:
            
            if mode == "cortical":
                cortFiles = np.sort(glob.glob("models/DK_atlas_pial/*"))
                painter = CorticalPainter(cortFiles)
                
            elif mode == "subcortical":
                cortFilesRight = np.sort(glob.glob("models/DK_atlas_pial/rh*"))
                subcortFiles = np.sort(glob.glob("models/subcortical_ply/*"))
                painter = SubcorticalPainter(cortFilesRight, subcortFiles)
                
            painter.prepareScene()
            painter.loadMeshes()

            
            for inputFile in INPUT_FILES_LONG:
                
                mat = np.genfromtxt(inputFile, delimiter=',') 
                print(mat)
                
                NR_REGIONS = mat.shape[0]
                NR_STAGES = mat.shape[1] + 1
                print(NR_REGIONS, NR_STAGES)
                
                colorRegionsAndRender(indexMap, NR_STAGES, NR_REGIONS, mat, OUT_FOLDER, inputFile)
            
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
            
if __name__ == "__main__":
    main()