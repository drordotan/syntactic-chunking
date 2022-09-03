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
                                  dependent_var='PMissingMorphemes', ylabel='Morpheme error rate',
                                  cond_factor='block', conditions=(1, 2, 3),
                                  out_fn=fig_dir+'block_mean_per_cond.pdf', ymax=0.38, d_y_ticks=.1, fig_size=(6, 2),
                                  xlim=(-1, 12),
                                  ds_names=['Condition A', 'Condition B', 'Condition C'], colors=GREENS, font_size=8, legend_title='Block')

#-- Figure: Learning within the first block (P:FigCmpBlockPart)
data['quartile'] = [(i-1) // 8 + 1 for i in data.ItemNum]
for i_cond, cond in enumerate(('A', 'B', 'C')):
    sc.plots.plot_performance_progress(data[data.Condition == cond],
                                       dependent_var='PMissingMorphemes', ylabel='Morpheme error rate',
                                       out_fn=fig_dir+'progress_cond{}.pdf'.format(cond),
                                       ymax=0.41, d_y_ticks=.1, fig_size=(4, 1),
                                       cond_names=dict(A='A (grammatical)', B='B', C='C (fragmented)'),
                                       colors=[GREENS[i_cond]],
                                       font_size=8,
                                       show_legend=False,
                                       show_xticks=i_cond == 2,
                                       xlabel='Time in experiment (block, quartile)' if i_cond == 2 else None
                                       )

#-- Figure: Comparison of conditions, single-subject level (P:FigCmpConds)
subj_grouping = [
    #-- Good effect (with bathtub): B < A, C
    (2, 13, 16, 18, 23,),
    (24, 26, 27, 28, 30,),

    #-- Good effect (no bathtub): A < B < C
    (5, 6, 12, 19, 35,),

    #-- No effect
    (9, 14, 17, 22,),  # A=B=C

    #-- Mismatching effects
    (10, 20, 33,),  # A > B > C
    (3, 7, 31, 32,),  # B > C, A
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
