#!/usr/bin/env python

import numpy as np
import os
import glob
import json #19/03/2018
from argparse import ArgumentParser #05/02/2018
import blendHelper

if __name__ == "__main__":
    
    parser = ArgumentParser(description="""A powerful tool for visualizing your brain data with Blender.
                                        Our implementation currently supports nothing.""")  
    
    subparsers = parser.add_subparsers(help="Method of data collection", dest="input_type")
    
    discrete = subparsers.add_parser("discrete", help="""Brain subdivided into discrete regions. For this method,
                                     we expect data matrices in .csv files where each row is a label, and each 
                                     column is an individual measurement. The labels are specified by the Blender
                                     models and the label mapping in your JSON file. Please note that your data 
                                     entries should be quantifiable.""")
    discrete.add_argument("-m", "--mode", choices=["cortical", "subcortical"], help="Type of Blender models used")
    discrete.add_argument("-l", "--labels", type=str, help="""JSON file with mapping from atlases to labels. 
                          Use -1 for any atlas which should be included in your images.""")
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
        
        with open(opt.labels, 'r') as f:
            indexMap = json.load(f)
            
        print(indexMap)

        for inputFile in INPUT_FILES_LONG:
        
            mat = np.genfromtxt(inputFile, delimiter=',') 
            print(mat)
            
            colorRegionsAndRender(indexMap, mats, OUT_FOLDER, inputFile)
        
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