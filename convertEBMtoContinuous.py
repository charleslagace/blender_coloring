import sys
import os
import numpy
import scipy.io
import argparse

parser = argparse.ArgumentParser(
  description='Convert EBM positional variance matrix from discreete to continuous (fine-grained approach)')

parser.add_argument('--inMat', dest="inMat", help='input positional variance matrix')

parser.add_argument('--outMat', dest="outMat", help='output positional variance matrix')

parser.add_argument('--levels', dest="levels", help='fine-grainnedness levels', type=int, default=250)


args = parser.parse_args()

mat = scipy.io.loadmat(args.inMat)
nrBiomk, nrStages = mat.shape[0]
nrLevels = args.levels
outMat = np.zeros((nrBiomk, nrLevels))

for b in range(nrBiomk):
  for l in range(args.levels):
    outMat[l] =

