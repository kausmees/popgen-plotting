import numpy as np
import pickle
import h5py
from pathlib import Path

DATA_PATH = "{0}/HO_data/".format(Path(__file__).resolve().parent)
STYLEFILE = "{0}/styles_HumanOrigins2067_filtered".format(DATA_PATH)
FAMFILE = "{0}/HumanOrigins2067_filtered".format(DATA_PATH)
SUPERPOPS_FILE = "{0}/HO_superpopulations".format(DATA_PATH)

UMAP_FINAL = "{0}umap.HumanOrigins2067_filtered.UMAP_N05_M05_S06.standard.flip_False.missing_val_-1.0.h5".format(DATA_PATH)
TSNE_FINAL = "{0}tsne.HumanOrigins2067_filtered.TSNE_L08_P02.standard.flip_False.missing_val_-1.0.h5".format(DATA_PATH)
GCAE_FINAL = "{0}encoded_data.h5".format(DATA_PATH)

def read_h5(filename, dataname):
	'''
	Read data from a h5 file.

	:param filename: directory and filename (with .h5 extension) of file to read from
	:param dataname: name of the datataset in the h5
	:return the data
	'''
	with h5py.File(filename, 'r') as hf:
		try:
			data = hf[dataname][:]
		except:
			# strange syntax to read a scalar value
			data = hf[dataname][()]
	return data

def get_ind_pop_list(filestart):
	'''
	Get a list of individuals and their populations from a .fam file.
	or if fam fiele does not exist, an .ind file
	:param filestart: directory and file prefix of file containing sample info
	:return: an (n_samples)x(2) list where ind_pop_list[n] = [individial ID, population ID] of the n:th individual
	'''
	try:
		ind_pop_list = np.genfromtxt(filestart + ".fam", usecols=(1,0), dtype=str)
	except:
		ind_pop_list = np.genfromtxt(filestart+".ind", usecols=(0,2), dtype=str)

		# # ugly and probably not general solution
		# if ":" in ind_pop_list[0][0]:
		# 	nlist = []
		# 	for v in ind_pop_list:
		# 		print(v)
		# 		v = v[0]
		# 		nlist.append(v.split(":")[::-1])
		# 	ind_pop_list = np.array(nlist)
	return ind_pop_list

def get_superpop_dict():
	'''
	Get a dict mapping superpopulation IDs to a list of their population IDs.

	:return:
	'''
	pop_superpop_list = np.genfromtxt(SUPERPOPS_FILE, usecols=(0,1), dtype=str, delimiter=",")
	superpops = np.unique(pop_superpop_list[:,1])
	superpop_dict = {}
	for spop in superpops:
		superpop_dict[spop] = []

	for i in range(len(pop_superpop_list)):
		superpop_dict[pop_superpop_list[i][1]].append(pop_superpop_list[i][0])

	return superpop_dict

def map_marker_to_bokeh(marker):
	'''
	Map the given matplotlib plot marker to a bokeh marker.

	:param marker: matplotlib marker
	:return: bokeh marker
	'''
	if marker == "o":
		return "o"
	if marker == "v":
		return "inverted_triangle"
	if marker == "<":
		return "diamond"
	if marker == "s":
		return "square"
	if marker == "p":
		return "triangle"
	if marker == "H":
		return "circle_cross"
	if marker == ">":
		return "asterisk"

def get_coords_by_pop(coords, ind_pop_list):
	'''
	Get the projected 2D coordinates specified by coords sorted by population.

	:param coords: a (n_samples) x 2 matrix of projected coordinates
	:param ind_pop_list: (n_samples) x 2 matric of individual ID, population ID for the samples of coords
	:return: a dict that maps a population name to a list of list of 2D-coordinates (one pair of coords for every sample in the population)

	'''
	try:
		new_list = []
		for i in range(len(ind_pop_list)):
			new_list.append([ind_pop_list[i][0].decode('UTF-8'), ind_pop_list[i][1].decode('UTF-8')])
		ind_pop_list = np.array(new_list)
	except:
		pass

	unique_pops = np.unique(ind_pop_list[:,1])
	pop_list = ind_pop_list[:,1]

	coords_by_pop = {}
	for p in unique_pops:
		coords_by_pop[p] = []

	for s in range(len(coords)):
		this_pop = pop_list[s]
		this_coords = coords[s]
		coords_by_pop[this_pop].append(this_coords)

	for p in unique_pops:
		coords_by_pop[p] = np.array(coords_by_pop[p])


	return coords_by_pop


def get_coords_final(model):
	'''
	Get coordinates of the final

	:return: dict mapping pop IDs => list of coordinates for the samples of that pop
	'''
	if model == "UMAP":
		projected_coords = read_h5(UMAP_FINAL, "coords")
	if model == "TSNE":
		projected_coords = read_h5(TSNE_FINAL, "coords")
	if model == "GCAE":
		projected_coords = read_h5(GCAE_FINAL, "180_encoded_train")


	ind_pop_list = get_ind_pop_list(FAMFILE)
	coords_by_pop = get_coords_by_pop(projected_coords, ind_pop_list)
	return coords_by_pop

def get_colors():
	style_list = get_style_list()
	return style_list[:,1]

def get_markers():
	return ['asterisk', 'circle_x', 'triangle']

def get_style_list():
	style_list = []
	with open("/home/kristiina/Projects/bokeh-interactive-scatter/interactive_scatter/data/styles_HumanOrigins2067_filtered.txt", "r") as ifile:
		for line in ifile:
			style_list.append([line.split(",")[0],line.split(",")[1],line.split(",")[2]])
	return np.array(style_list)


def get_style_dict():
	'''
	Get a dict mapping population IDs to a list of styles for a scatterplot.
	A style is a list of 3 items: [marker, color, edge_color]

	:return: style dict, mapping str => [str, str, str]

	'''

	with open(STYLEFILE, 'rb') as stylefile:
		style_dict = pickle.load(stylefile)
	for key in style_dict:
		style_dict[key] = [map_marker_to_bokeh(style_dict[key][0]), style_dict[key][1], style_dict[key][2]]
		# print(key, '=>', style_dict[key])
	return style_dict
