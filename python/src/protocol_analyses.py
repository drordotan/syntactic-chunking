
import pandas as pd
import sc
import matplotlib as mpl


mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42

d = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking Nadin/data/'
fig_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking Nadin/figures/'

RED = '#BF5860'
GREENS = ('#455C41', '#62845C', '#79A472', '#A2D49A')
GREEN = GREENS[2]

#--------------------------------------------------------------------------------------------------
#  Experiment 1 & 2
#--------------------------------------------------------------------------------------------------

cond_names_exp1_blocked = None

exp12 = pd.read_excel(d+'exp1&2/data_coded.xlsx')
exp1 = exp12[exp12.Condition.isin(['A', 'B', 'C', 'D'])]
exp2 = exp12[exp12.Condition.isin(range(10))]

#-- Blocked (PStat:FigExp1BlockedConds)
sc.plots.plot_cond_means_multiple_measures(exp1, dependent_vars=['PMissingMorphemes', 'PMissingDigits', 'PMissingClasses'],
                                           out_fn=fig_dir+'exp1_cond_mean_all.pdf', ymax=0.3, d_y_ticks=.05, fig_size=(6, 2),
                                           cond_names=dict(A='A (grammatical)', B='B', C='C', D='D (fragmented)'), conditions=('A', 'B', 'C', 'D'),
                                           dependent_var_names=('Morpheme errors', 'Digit errors', 'Class errors'), colors=GREENS, font_size=8)
'''
sc.plots.plot_cond_means(exp1_blocked, 'PMissingWords', fig_dir+ 'exp1_blocked_cond_mean_words.png', ymax=0.3, fig_size=(4, 2),
                         cond_names=cond_names_exp1_blocked)
sc.plots.plot_cond_means(exp1_blocked, 'PMissingDigits', fig_dir+ 'exp1_blocked_cond_mean_digits.png', ymax=0.2, dy=.05, fig_size=(4, 2),
                         cond_names=cond_names_exp1_blocked)
sc.plots.plot_cond_means(exp1_blocked, 'PMissingClasses', fig_dir+ 'exp1_blocked_cond_mean_classes.png', ymax=0.05, dy = .01, fig_size=(4, 2),
                         cond_names=cond_names_exp1_blocked)
'''

#-- Per subject (PStat:FigExp1PerSubj)

#sc.analyze.exp1_auto_group_subjects(exp1_blocked, 'PMissingWords')
subj_grouping = [
    (12, 13, 17, 19),
    (6, 15, 16, 20),
    (2, 10, 11),
    (3, 7, 8, 18),
    (1, 4, 5, 14),
    (9, ),
]


sc.plots.plot_cond_means_per_subject(exp1, 'PMissingMorphemes', fig_dir+'exp1_per_subj_morph.pdf', ymax=0.42, fig_size=(6, 6),
                                     subj_grouping=subj_grouping, y_label='Morpheme error rate')

sc.plots.plot_cond_means_per_subject(exp1, 'PMissingDigits', fig_dir+'exp1_per_subj_digit.pdf', ymax=0.42, fig_size=(6, 6),
                                     subj_grouping=subj_grouping, y_label='Morpheme error rate')

sc.plots.plot_cond_means_per_subject(exp1, 'PMissingClasses', fig_dir+'exp1_per_subj_class.pdf', ymax=0.42, fig_size=(6, 6),
                                     subj_grouping=subj_grouping, y_label='Morpheme error rate')

#-- Compare % of specific items that are better in each condition (PStat:Exp1ComparePerItem)
sc.analyze.compare_conds_per_item(exp1, 'D', 'B', 'PMissingMorphemes')


#  Experiment 2: Mixed
#-------------------------

#-- Mixed (PStat:FigExp1MixedConds)
sc.plots.plot_cond_means_multiple_measures(exp2, dependent_vars=['PMissingMorphemes', 'PMissingDigits', 'PMissingClasses'],
                                           out_fn=fig_dir+'exp2_cond_mean_all.pdf', ymax=0.349, d_y_ticks=.05, fig_size=(6, 2),
                                           cond_names={2: '2 segments', 3: '3 segments', 4: '4 segments'}, conditions=(2, 3, 4),
                                           dependent_var_names=('Morpheme errors', 'Digit errors', 'Class errors'), colors=GREENS[1:], font_size=8)

sc.plots.plot_2cond_means_per_subject(exp2, 'PMissingMorphemes', fig_dir+'exp2_per_subj_morph.pdf', ymax=0.42, fig_size=(6, 6),
                                      cond_names={2:'Grammatical (2 seg.)', 4:'Fragmented (4 seg.)'}, conds=[2, 4])



#--------------------------------------------------------------------------------------------------
#  Experiment 3
#--------------------------------------------------------------------------------------------------


exp3 = pd.read_excel(d+'exp3/data_coded.xlsx')

#-- (PStat:FigExp3Conds)
sc.plots.plot_cond_means_multiple_measures(exp3, dependent_vars=['PMissingMorphemes', 'PMissingDigits', 'PMissingClasses'],
                                           out_fn=fig_dir+'exp3_cond_mean_all.pdf', ymax=0.4, d_y_ticks=.05, fig_size=(4, 2),
                                           cond_names=dict(A='Grammatical', B='Fragmented'), conditions=('A', 'B'),
                                           cond_comparison_text=[['***'], ['***'], ['***']],
                                           dependent_var_names=('Morpheme errors', 'Digit errors', 'Class errors'), colors=(GREEN, RED), font_size=8)
#-- (PStat:FigExp2PerSubj)
'''
exp3_cond_names = dict(A='Syntactic', B='Non-Syntactic')
sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingWords', fig_dir+'exp2_per_subj_words.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp3_cond_names)
sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingDigits', fig_dir+'exp2_per_subj_digits.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp3_cond_names)
sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingClasses', fig_dir+'exp2_per_subj_classes.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp3_cond_names)
'''

#-- (PStat:FigExp3PerSubj)
sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingMorphemes', fig_dir+'exp3_per_subj_morph.pdf', ymax=0.42, fig_size=(6, 6),
                                      cond_names=dict(A='Grammatical', B='Fragmented'))
sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingDigits', fig_dir+'exp3_per_subj_digit.pdf', ymax=0.42, fig_size=(6, 6),
                                      cond_names=dict(A='Grammatical', B='Fragmented'))
sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingClasses', fig_dir+'exp3_per_subj_class.pdf', ymax=0.42, fig_size=(6, 6),
                                      cond_names=dict(A='Grammatical', B='Fragmented'))

#-- Compare % of specific items that are better in each condition (PStat:Exp3ComparePerItem)
sc.analyze.compare_conds_per_item(exp3, 'A', 'B', 'PMissingMorphemes')

#--------------------------------------------------------------------------------------------------
#  Experiment 4
#--------------------------------------------------------------------------------------------------


exp4 = pd.read_excel(d+'exp4/data_coded.xlsx')

sc.plots.plot_cond_means_multiple_measures(exp4, dependent_vars=['PMissingMorphemes', 'PMissingDigits', 'PMissingClasses'],
                                           out_fn=fig_dir+'exp4_cond_mean_all.pdf', ymax=0.4, d_y_ticks=.05, fig_size=(4, 2),
                                           cond_names=dict(A='Grammatical', B='Fragmented'), conditions=('A', 'B'),
                                           cond_comparison_text=[['***'], ['***'], ['***']],
                                           dependent_var_names=('Morpheme errors', 'Digit errors', 'Class errors'), colors=(GREEN, RED), font_size=8)

#-- (PStat:FigExp3PerSubj)
sc.plots.plot_2cond_means_per_subject(exp4, 'PMissingMorphemes', fig_dir+'exp4_per_subj_morph.pdf', ymax=0.42, fig_size=(6, 6),
                                      cond_names=dict(A='Grammatical', B='Fragmented'))
sc.plots.plot_2cond_means_per_subject(exp4, 'PMissingDigits', fig_dir+'exp4_per_subj_digit.pdf', ymax=0.42, fig_size=(6, 6),
                                      cond_names=dict(A='Grammatical', B='Fragmented'))
sc.plots.plot_2cond_means_per_subject(exp4, 'PMissingClasses', fig_dir+'exp4_per_subj_class.pdf', ymax=0.42, fig_size=(6, 6),
                                      cond_names=dict(A='Grammatical', B='Fragmented'))

#-- Compare % of specific items that are better in each condition (PStat:Exp3ComparePerItem)
sc.analyze.compare_conds_per_item(exp4, 'A', 'B', 'PMissingMorphemes')

#-- (PStat:FigExp3Conds)
'''
exp4_cond_names = dict(A='Syntactic', B='Non-Syntactic')
sc.plots.plot_2cond_means_per_subject(exp, 'PMissingWords', fig_dir+'exp4_per_subj_words.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp4_cond_names)
sc.plots.plot_2cond_means_per_subject(exp, 'PMissingDigits', fig_dir+'exp4_per_subj_digits.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp4_cond_names)
sc.plots.plot_2cond_means_per_subject(exp, 'PMissingClasses', fig_dir+'exp4_per_subj_classes.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp4_cond_names)
'''