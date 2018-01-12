import matplotlib.pyplot as plt
import matplotlib as mpl

width=10
height=10
# Make a figure and axes with dimensions as desired.
fig = plt.figure(figsize=(width, height))
ax1 = fig.add_axes([0.05, 0.80, 0.9, 0.15])
# Set the colormap and norm to correspond to the data for which
# the colorbar will be used.
cmap=plt.get_cmap('Reds')
norm = mpl.colors.Normalize(vmin=0, vmax=255)

# ColorbarBase derives from ScalarMappable and puts a colorbar
# in a specified axes, so it has everything needed for a
# standalone colorbar.  There are many more kwargs, but the
# following gives a basic continuous colorbar with ticks
# and labels.
cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap,
                                norm=norm,
                                orientation='horizontal')
cb1.set_label('')
# The second example illustrates the use of a ListedColormap, a
# BoundaryNorm, and extended ends to show the "over" and "under"
# value colors.
cmap = mpl.colors.ListedColormap(['r', 'g', 'b', 'c'])
cmap.set_over('0.25')
cmap.set_under('0.75')

# If a ListedColormap is used, the length of the bounds array must be
# one greater than the length of the color list.  The bounds must be
# monotonically increasing.
plt.savefig('foo.png')

