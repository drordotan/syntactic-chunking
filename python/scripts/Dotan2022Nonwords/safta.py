import pandas as pd
import sc
import matplotlib as mpl


mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

d = '/Users/dror/data/acad-proj/3-Submitted/syntactic chunking nonwords/data/'
fig_dir = '/Users/dror/data/acad-proj/3-Submitted/syntactic chunking nonwords/figures/'

RED = '#BF5860'
GREEN = '#62845C'


data = pd.read_excel(d+'data_clean.xlsx')

sc.plots.plot_cond_means_multiple_measures(data, dependent_vars=['PMissingMorphemes'],
                                           out_fn=fig_dir+'safta.pdf', ymax=0.38, d_y_ticks=.1, fig_size=(3, 2),
                                           cond_names=dict(B='Grammatical', C='Non-grammatical'), conditions=('B', 'C'),
                                           dependent_var_names=('Morpheme errors',), colors=[GREEN, RED], font_size=8,
                                           show_legend=False)
