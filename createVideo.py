{\rtf1\ansi\ansicpg1252\cocoartf1504\cocoasubrtf830
{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;\red0\green0\blue0;}
{\*\expandedcolortbl;;\cssrgb\c0\c0\c0;}
\paperw11900\paperh16840\margl1440\margr1440\vieww10800\viewh8400\viewkind0
\deftab720
\pard\pardeftab720\partightenfactor0

\f0\fs24 \cf0 \expnd0\expndtw0\kerning0
def merge_files(dir_name, output):\
    ff_mpg = 'ffmpeg -start_number 0 -i %s/cortical_stage%03d.png' % dir_name\
    ff_mpg += ' -c:v libx264 -vf fps=25,format=yuv420p '\
    ff_mpg += output\
    ff_mpg += '.mp4'\
    r = subprocess.call(ff_mpg)\
    return r\
\
\
def main():\
    merge_files('output/alex16Aug2016/ADNI1pt5T/PVD_group1', 'test')\
\
\
if __name__ == '__main__':\
    main()\
}