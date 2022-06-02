import pandas as pd
import sc
import matplotlib as mpl


mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

d = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/data/'
fig_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/figures/'

RED = '#BF5860'
GREENS = ('#455C41', '#62845C', '#79A472', '#A2D49A')
GREEN = GREENS[2]


data = pd.read_excel(d+'data_coded.xlsx')


sc.plots.plot_cond_means_multiple_measures(data, dependent_vars=['PMissingMorphemes', 'PMissingDigits', 'PMissingClasses'],
                                           out_fn=fig_dir+'cond_mean_all.pdf', ymax=0.38, d_y_ticks=.1, fig_size=(6, 2),
                                           cond_names=dict(A='A (grammatical)', B='B', C='C (fragmented)'), conditions=('A', 'B', 'C'),
                                           dependent_var_names=('Morpheme errors', 'Digit errors', 'Class errors'), colors=GREENS, font_size=8)


subj_grouping = [
    ('SC11', 'SC12'),  # 'SC', 'SC'),
    ('SC5', 'SC6', 'SC7', 'SC8'),
    ('SC13', 'SC16', 'SC18'),
    ('SC10', ),
    # ('SC3', 'SC17', 'SC9'),
]

sc.plots.plot_cond_means_per_subject(data, 'PMissingMorphemes', fig_dir+'per_subj_morph.pdf', ymax=0.42, fig_size=(6, 6),
                                      y_label='Morpheme error rate', subj_grouping=subj_grouping)
