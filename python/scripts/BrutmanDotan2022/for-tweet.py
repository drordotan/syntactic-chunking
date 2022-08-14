
import pandas as pd
import sc
import matplotlib as mpl


mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

d = '/Users/dror/data/acad-proj/4-Published/2022 syntactic chunking Nadin/data/'
fig_dir = '/Users/dror/data/acad-proj/4-Published/2022 syntactic chunking Nadin/figures/'

RED = '#BF5860'
GREENS = ('#455C41', '#62845C', '#79A472', '#A2D49A')
GREEN = GREENS[2]

supp_fig_per_subj_size = (8, 6)

#--------------------------------------------------------------------------------------------------
#  Experiments 1 & 2
#--------------------------------------------------------------------------------------------------

cond_names_exp1_blocked = None

exp12 = pd.read_excel(d+'exp1&2/data_coded.xlsx')
exp1 = exp12[exp12.Condition.isin(['A', 'B', 'C', 'D'])]

#-- Blocked (PStat:FigExp1BlockedConds)
sc.plots.plot_cond_means(exp1, dependent_var='PMissingMorphemes',
                         out_fn=fig_dir+'tweet_exp1.pdf', ymax=0.18, fig_size=(4, 2), dy=0.05,
                         cond_names=dict(A='Fully\ngrammatical', B='', C='', D='Fully\nfragmented'),
                         colors=GREENS)

