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
