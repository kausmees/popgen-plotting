from bokeh.models import BoxSelectTool, LassoSelectTool, Legend
from bokeh.plotting import figure
from bokeh.layouts import column, row
from ..data.data_loader import get_coords_final, get_style_dict, get_superpop_dict


def legend_scatter_HO():
	'''
	Bokeh scatterplot of dimensionality reduction results for the HumanOigins data, color-coded by population and superpopulation.
	One legend per superpopulation.

	:return: a bokeh layout
	'''
	coords_by_pop = get_coords_final("GCAE")
	superpop_dict = get_superpop_dict()
	style_dict = get_style_dict()

	spops = ["Sub-Saharan Africa",  "Americas", "Oceania", "Middle East", "East Asia", "North Asia", "Europe", "Central/South Asia"]

	TOOLS="pan,wheel_zoom,reset"

	plot = figure(tools=TOOLS,
				  width=1000,
				  height=800,
				  toolbar_location="above",
				  x_axis_location=None,
				  y_axis_location=None,
				  sizing_mode='stretch_both',
				  title="GCAE")

	plot.background_fill_color = "#fafafa"

	plot.select(BoxSelectTool).select_every_mousemove = False
	plot.select(LassoSelectTool).select_every_mousemove = False

	# maps population IDs to renderer objects
	pop_renderers = {}

	for spop in spops:
		for pop in superpop_dict[spop]:
			coords = coords_by_pop[pop]
			x = coords[:,0]
			y = coords[:,1]
			style = style_dict[pop]
			r = plot.scatter(x, y,
							 size=10,
							 marker=style[0],
							 color=style[1],
							 alpha=1.0,
							 line_color=style[2],
							 muted_color="gray",
							 muted_alpha=0.2)
			pop_renderers[pop] = r

	# maps superpopulations IDs to legend-item lists
	spop_legend_items = {}

	for spop in spops:
		spop_legend_items[spop] = [(pop,[pop_renderers[pop]]) for pop in superpop_dict[spop]]

	legend_width = 230

	# maps superpopulations IDs to figures
	spop_figs = {}

	# workaround to have separate legends that can be placed as layout objects
	for spop in spops:
		num_pops = len(superpop_dict[spop])
		this_leg_fig = figure(height=num_pops * 35 + 55,
							  width = legend_width + 20,
							  outline_line_alpha = 0,
							  toolbar_location = None)

		for component in [this_leg_fig.grid[0],this_leg_fig.ygrid[0],this_leg_fig.xaxis[0],this_leg_fig.yaxis[0]]:
			component.visible = False

		this_leg_fig.renderers += [pop_renderers[pop] for pop in superpop_dict[spop]]
		this_leg_fig.x_range.end = -1.0
		this_leg_fig.x_range.start = -2.0
		this_leg_fig.add_layout(Legend(click_policy='hide',
									   location='top_left',
									   label_text_font_size="15pt",
									   items=spop_legend_items[spop],
									   label_width=legend_width))
		spop_figs[spop] = this_leg_fig


	for spop in spops:
		spop_figs[spop].legend.glyph_width=30
		spop_figs[spop].legend.glyph_height=30

	final = row(plot,
				column([spop_figs[spop] for spop in ["Sub-Saharan Africa", "Americas"]]),
				column([spop_figs[spop] for spop in ["East Asia", "Oceania"]]),
				column([spop_figs[spop] for spop in ["Middle East", "North Asia"]]),
				column([spop_figs[spop] for spop in ["Europe"]]),
				column([spop_figs[spop] for spop in ["Central/South Asia"]])
				)

	return final

