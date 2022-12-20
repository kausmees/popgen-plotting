import numpy as np
from bokeh.layouts import column, row
from bokeh.models import CustomJS, Slider, BoxSelectTool, LassoSelectTool, Div
from bokeh.plotting import ColumnDataSource, figure, output_file, show
from bokeh.models.formatters import PrintfTickFormatter, FuncTickFormatter
from ..data.data_loader import get_coords_by_hyperparam, get_coords_final, get_style_dict, get_superpop_dict

def hyperparam_eval_scatter(model="TSNE"):

	if model == "PCA":
		xlabel = "PC2"
		ylabel = "PC1"

	elif model == "popvae":
		xlabel = "D1"
		ylabel = "D2"

	elif model == 'UMAP':
		xlabel = "D2"
		ylabel = "D1"
		slider1_title = 'n_neighbors'
		slider1_ticks = [3, 5, 10, 20, 50, 100, 200]

		slider2_title = 'min_dist'
		slider2_ticks = [0.05, 0.1, 0.25, 0.5, 0.75, 1.0]

		slider3_title = 'spread'
		slider3_ticks = [0.05, 0.1, 0.25, 0.5, 0.75, 1.0]  # 6
		slider3_visible = True

	elif model == 'TSNE':
		xlabel = "D2"
		ylabel = "D1"
		slider1_title = 'learning_rate'
		slider1_ticks = [43, 170, 200, 225, 250, 300, 350, 400, 450, 500, 650, 600]

		slider2_title = 'perplexity'
		slider2_ticks = [5, 10, 20, 30, 45, 50, 75, 100, 125, 175, 200]

		slider3_title = 'none'
		slider3_ticks = [0.1, 1.0]  # 6
		slider3_visible = False

	elif model == 'ISOMAP':
		xlabel = "D2"
		ylabel = "D1"
		slider1_title = 'n_neighbors'
		slider1_ticks = [5, 10, 20, 30, 45, 50, 75,100, 125, 175, 200]

		slider2_title = 'p'
		slider2_ticks = [1, 2, 5]

		slider3_title = 'none'
		slider3_ticks = [0.1, 1.0]  # 6
		slider3_visible = False


	s1_startval = 1
	s2_startval = 1
	s3_startval = 1


	s1_formatter = FuncTickFormatter(code="""
	    var labels = %s;
	    return labels[tick-1];
	""" % slider1_ticks)

	s2_formatter = FuncTickFormatter(code="""
	    var labels = %s;
	    return labels[tick-1];
	""" % slider2_ticks)

	s3_formatter = FuncTickFormatter(code="""
	    var labels = %s;
	    return labels[tick-1];
	""" % slider3_ticks)

	if model=="TSNE":
		s1_initval = 9
	else:
		s1_initval = 1

	s2_initval=1
	s3_initval=len(slider3_ticks)
	slider1 = Slider(start=s1_startval, end=len(slider1_ticks), value=s1_initval, step=1, title=slider1_title, format=s1_formatter)
	slider2 = Slider(start=s2_startval, end=len(slider2_ticks), value=s2_initval, step=1, title=slider2_title, format=s2_formatter)
	slider3 = Slider(start=s3_startval, end=len(slider3_ticks), value=s3_initval, step=1, title=slider3_title, format=s3_formatter, visible=slider3_visible)


	TOOLS="pan,wheel_zoom,box_zoom,save,reset"
	plot = figure(tools=TOOLS,
				  width=600,
				  height=600,
				  x_axis_label=xlabel,
				  y_axis_label=ylabel,
				  toolbar_location="above",
				  x_axis_location=None,
				  y_axis_location=None,
				  title=model)

	# plot.background_fill_color = "#ffffff"
	plot.xgrid.visible = False
	plot.ygrid.visible = False
	plot.xaxis.visible = False
	plot.yaxis.visible = False
	plot.background_fill_color = None
	plot.border_fill_color = None


	plot.select(BoxSelectTool).select_every_mousemove = False
	plot.select(LassoSelectTool).select_every_mousemove = False

	coords_by_pop = get_coords_by_hyperparam(model, s1_initval, s2_initval, s3_initval)
	superpop_dict = get_superpop_dict()
	style_dict = get_style_dict()

	spops = ["Sub-Saharan Africa",  "Americas", "Oceania", "Middle East", "East Asia", "North Asia", "Europe", "Central/South Asia"]

	# # maps population IDs to renderer objects
	pop_renderers = {}

	for spop in spops:

		for pop in superpop_dict[spop]:
			coords = coords_by_pop[pop]

			if (model == "popvae"):
				x = coords[:,0]
				y = coords[:,1]

			else:
				x = coords[:,1]
				y = coords[:,0]

			style = style_dict[pop]
			r = plot.scatter(x, y,
							 size=10,
							 marker=style[0],
							 color=style[1],
							 alpha=1.0,
							 line_color=style[2],
							 line_width=0.4,
							 muted_color="gray",
							 muted_alpha=0.2)
			pop_renderers[pop] = r



	callback = CustomJS(args=dict(sources=pop_renderers, model=model, s1=slider1, s2=slider2, s3=slider3),
						code="""
		 $.ajax({
				url:'./_get_data',
				type:'post',
				data:{'model':model, 's1_val':s1.value, 's2_val':s2.value, 's3_val':s3.value},
				success : function(data){

				const new_coords_by_pop = JSON.parse(data);
				const s1_val = s1.value;
				const s2_val = s2.value;
				const s3_val = s3.value;

				for (var pop in sources) {
					var source = sources[pop];
					console.log(source);
					const data = source.data_source.data;
					const new_coords_this_pop = new_coords_by_pop[pop];
					
					const x = data['x'];
					const y = data['y'];
					// TODO map or slice or something instead of loop
					for (var i = 0; i < x.length; i++) {
						x[i] = new_coords_this_pop[i][0];
						y[i] = new_coords_this_pop[i][1];
					}
					source.data_source.change.emit();
				}
			}
		});
	""")

	slider1.js_on_change('value', callback)
	slider2.js_on_change('value', callback)
	slider3.js_on_change('value', callback)

	layout = row(
		column(slider1, slider2, slider3),
		Div(text='<div style="background-color: None; width: 30px; height: 0px;"></div>'),
		plot,
	)

	return layout