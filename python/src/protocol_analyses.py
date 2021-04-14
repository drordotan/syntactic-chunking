
import pandas as pd
import sc

d = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking Nadin/data/'
fig_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking Nadin/figures/'

#--------------------------------------------------------------------------------------------------
#  Experiment 1
#--------------------------------------------------------------------------------------------------

cond_names_exp1_blocked = None

exp1 = pd.read_excel(d+'exp1/data_coded.xlsx')
exp1_blocked = exp1[exp1.Condition.isin(['A', 'B', 'C', 'D'])]
exp1_mixed = exp1[exp1.Condition.isin(range(10))]

#-- Blocked (PStat:FigExp1BlockedConds)
sc.plots.plot_cond_means(exp1_blocked, 'PMissingWords', fig_dir+ 'exp1_blocked_cond_mean_words.png', ymax=0.3, fig_size=(4, 2),
                         cond_names=cond_names_exp1_blocked)
sc.plots.plot_cond_means(exp1_blocked, 'PMissingDigits', fig_dir+ 'exp1_blocked_cond_mean_digits.png', ymax=0.2, dy=.05, fig_size=(4, 2),
                         cond_names=cond_names_exp1_blocked)
sc.plots.plot_cond_means(exp1_blocked, 'PMissingClasses', fig_dir+ 'exp1_blocked_cond_mean_classes.png', ymax=0.05, dy = .01, fig_size=(4, 2),
                         cond_names=cond_names_exp1_blocked)

#-- Mixed (PStat:FigExp1MixedConds)
sc.plots.plot_cond_means(exp1_mixed, 'PMissingWords', fig_dir + 'exp1_mixed_cond_mean_words.png', ymax=0.4, fig_size=(3, 2))
sc.plots.plot_cond_means(exp1_mixed, 'PMissingDigits', fig_dir + 'exp1_mixed_cond_mean_digits.png', ymax=0.25, dy=.05, fig_size=(3, 2))
sc.plots.plot_cond_means(exp1_mixed, 'PMissingClasses', fig_dir + 'exp1_mixed_cond_mean_classes.png', ymax=0.25, dy=.05, fig_size=(3, 2))



#-- Per subject (PStat:FigExp1PerSubj)

#sc.analyze.exp1_auto_group_subjects(exp1_blocked, 'PMissingWords')

subj_grouping = [
    ('19ENCH', '12MICH', '13AYZO'),
    ('16DAER', '20NTMB', '2OSAN'),
    ('4ANTR', '17INAV', '9ORMN',),
    ('5DFGN', '10BRAS', '11ILAX', '18TASH',),
    ('3ROBE', '7INLU', '8TAYA', '6ENGO',),
    ('14ELYA',),
    ('15SHFA', '1MICO',),
]

sc.plots.plot_cond_means_per_subject(exp1_blocked, 'PMissingWords', fig_dir+ 'exp1_blocked_per_subj_words.pdf', ymax=0.42, fig_size=(6, 8),
                                     cond_names=cond_names_exp1_blocked,
                                     subj_grouping=subj_grouping)

sc.plots.plot_cond_means_per_subject(exp1_blocked, 'PMissingDigits', fig_dir+ 'exp1_blocked_per_subj_digits.pdf', ymax=0.42, fig_size=(6, 8),
                                     cond_names=cond_names_exp1_blocked,
                                     subj_grouping=subj_grouping)

sc.plots.plot_cond_means_per_subject(exp1_blocked, 'PMissingClasses', fig_dir+ 'exp1_blocked_per_subj_classes.pdf', ymax=0.25, fig_size=(6, 8),
                                     cond_names=cond_names_exp1_blocked,
                                     subj_grouping=subj_grouping)


#--------------------------------------------------------------------------------------------------
#  Experiment 2
#--------------------------------------------------------------------------------------------------

exp2_cond_names = dict(A='Syntactic', B='Non-Syntactic')

exp2 = pd.read_excel(d+'exp2/data_coded.xlsx')

#-- (PStat:FigExp2Conds)
sc.plots.plot_cond_means(exp2, 'PMissingWords', fig_dir + 'exp2_cond_mean_words.png', ymax=0.4, fig_size=(4, 3), cond_names=exp2_cond_names)
sc.plots.plot_cond_means(exp2, 'PMissingDigits', fig_dir + 'exp2_cond_mean_digits.png', ymax=0.3, dy=.05,  fig_size=(4, 2), cond_names=exp2_cond_names)
sc.plots.plot_cond_means(exp2, 'PMissingClasses', fig_dir + 'exp2_cond_mean_classes.png', ymax=0.15, dy=.05, fig_size=(4, 2), cond_names=exp2_cond_names)

#-- (PStat:FigExp2PerSubj)
sc.plots.plot_2cond_means_per_subject(exp2, 'PMissingWords', fig_dir+ 'exp2_per_subj_words.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp2_cond_names)
sc.plots.plot_2cond_means_per_subject(exp2, 'PMissingDigits', fig_dir+ 'exp2_per_subj_digits.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp2_cond_names)
sc.plots.plot_2cond_means_per_subject(exp2, 'PMissingClasses', fig_dir+ 'exp2_per_subj_classes.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp2_cond_names)


#--------------------------------------------------------------------------------------------------
#  Experiment 3
#--------------------------------------------------------------------------------------------------

exp3_cond_names = dict(A='Syntactic', B='Non-Syntactic')

exp3 = pd.read_excel(d+'exp3/data_coded.xlsx')

#-- (PStat:FigExp3Conds)
sc.plots.plot_cond_means(exp3, 'PMissingWords', fig_dir + 'exp3_cond_mean_words.png', ymax=0.4, fig_size=(4, 3), cond_names=exp2_cond_names)
sc.plots.plot_cond_means(exp3, 'PMissingDigits', fig_dir + 'exp3_cond_mean_digits.png', ymax=0.3, dy=.05,  fig_size=(4, 2), cond_names=exp2_cond_names)
sc.plots.plot_cond_means(exp3, 'PMissingClasses', fig_dir + 'exp3_cond_mean_classes.png', ymax=0.25, dy=.05, fig_size=(4, 2), cond_names=exp2_cond_names)

sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingWords', fig_dir+ 'exp3_per_subj_words.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp3_cond_names)
sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingDigits', fig_dir+ 'exp3_per_subj_digits.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp3_cond_names)
sc.plots.plot_2cond_means_per_subject(exp3, 'PMissingClasses', fig_dir+ 'exp3_per_subj_classes.pdf', ymax=0.48, fig_size=(7, 3), cond_names=exp3_cond_names)
