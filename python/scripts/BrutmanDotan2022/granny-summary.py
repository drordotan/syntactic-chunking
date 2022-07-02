
import pandas as pd
import sc
import matplotlib as mpl


mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

d = '/Users/dror/data/acad-proj/4-Published/2022 syntactic chunking Nadin/data/'
fig_dir = '/Users/dror/data/acad-proj/4-Published/2022 syntactic chunking Nadin/figures/'


exp12 = pd.read_excel(d+'exp1&2/data_coded.xlsx')
exp1 = exp12[exp12.Condition.isin(['B', 'D'])]

#-- Blocked (PStat:FigExp1BlockedConds)
sc.plots.plot_cond_means_multiple_measures(exp1, dependent_vars=['PMissingMorphemes'],
                                           out_fn=fig_dir+'granny_fig1.pdf', ymax=0.24, d_y_ticks=.05, fig_size=(3, 2),
                                           cond_names=dict(B='Grammatical)', D='Non-grammatical'), conditions=('B', 'D'), show_legend=False,
                                           dependent_var_names=('Sequence type', ), colors=('#79A472', '#BF5860'), font_size=8)
