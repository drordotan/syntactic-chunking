import pandas as pd
import sc
import matplotlib as mpl


mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

d = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/data/'
fig_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/figures/'

RED = '#BF5860'
GREENS = ('#455C41', '#62845C', '#79A472', '#A2D49A', '#C1F7B8')
GREEN = GREENS[2]


data = pd.read_excel(d+'data_clean.xlsx')


#-- Figure: Comparison of conditions (P:FigCmpConds)
sc.plots.plot_cond_means_multiple_measures(data, dependent_vars=['PMissingMorphemes', 'PMissingDigits', 'PMissingClasses'],
                                           out_fn=fig_dir+'cond_mean_all.pdf', ymax=0.38, d_y_ticks=.1, fig_size=(8, 2),
                                           cond_names=dict(A='A (grammatical)', B='B', C='C (fragmented)'), conditions=('A', 'B', 'C'),
                                           dependent_var_names=('Morpheme errors', 'Stem errors', 'Class errors'), colors=GREENS, font_size=8)


#-- Figure: Learning from block to block  (P:FigCmpBlocks)
sc.plots.plot_cond_means_multiple([data[data.Condition == 'A'], data[data.Condition == 'B'], data[data.Condition == 'C']],
                                  dependent_var='PMissingMorphemes',
                                  cond_factor='block', conditions=(1, 2, 3),
                                  out_fn=fig_dir+'block_mean_per_cond.pdf', ymax=0.38, d_y_ticks=.1, fig_size=(6, 2),
                                  xlim=(-1, 12),
                                  ds_names=['Condition A', 'Condition B', 'Condition C'], colors=GREENS, font_size=8, legend_title='Block')

#-- Figure: Comparison of conditions, single-subject level (P:FigCmpConds)
subj_grouping = [
    #-- B < A, C
    ('SC16', 'SC23', 'SC18', 'SC13',),
    ('SC23', 'SC24', 'SC27', 'SC2',  ),

    ( 'SC6', 'SC7', 'SC8', 'SC19', 'SC12', 'SC5',), #-- A < B < C

    ('SC17',  'SC9', 'SC22', ),  # A=B=C

    #-- Mismatches
    ('SC10', 'SC20', ),  # A > B > C
    ('SC3', ),  # B > C, A
]

sc.plots.plot_cond_means_per_subject(data, 'PMissingMorphemes', fig_dir+'per_subj_morph.pdf', ymax=0.52, fig_size=(6, 6),
                                     y_label='Morpheme error rate', subj_grouping=subj_grouping, colors=('black', ) + GREENS)


#--------- Not in ms.

#-- Analysis of word order
datawords = pd.read_csv(d+'data_coded_words.csv')

sc.plots.plot_digit_accuracy_per_position(datawords, save_as=fig_dir+'acc_per_pos_new.pdf',
                                          conditions=['A', 'B', 'C'], cond_names=['A (grammatical)', 'B', 'C (fragmented)'],
                                          colors=GREENS, ylim=(0, .8), d_y_ticks=0.1, fig_size=(6, 3), font_size=12,
                                          marker_text=(('T', 'H', 'N', 'O'),
                                                       ('N', 'O', 'T', 'H'),
                                                       ('O', 'N', 'H', 'T')))

sc.plots.plot_digit_accuracy_per_position(datawords, save_as=fig_dir+'acc_per_class_new.pdf',
                                          conditions=['A', 'B', 'C'], cond_names=['A (grammatical)', 'B', 'C (fragmented)'],
                                          pos_field='word_class_order',
                                          colors=GREENS, ylim=(0, .8), d_y_ticks=0.1, fig_size=(6, 3), font_size=12,
                                          marker_text=(('T', 'H', 'N', 'O'),
                                                       ('N', 'O', 'T', 'H'),
                                                       ('O', 'N', 'H', 'T')))
