library(lme4)
library(car)
library(zeallot)
library(dplyr)
library(purrr)
library(stringr)
library(effects)
library(gdata)
library(sjPlot)
library(plyr)

scripts_dir = '/Users/dror/git/syntactic-chunking/R-syntactic-chunking'
data_dir = '/Users/dror/data/acad-proj/3-Submitted/syntactic chunking Nadin/data'
models_dir = '/Users/dror/data/acad-proj/3-Submitted/syntactic chunking Nadin/figures/models'

source(paste(scripts_dir, 'utils.R', sep='/'))
source(paste(scripts_dir, 'sc_basic.R', sep='/'))

Sys.setenv("R_IS_ASSIGNING" = 0)

#--------------------------------------------------------------------------
# Experiment 1 & 2
#--------------------------------------------------------------------------

sdata12 = load_data(paste(data_dir, 'exp1&2/data_coded.csv', sep='/'))
sdata1 = sdata12[sdata12$Block != 'R',]
sdata2 = sdata12[sdata12$Block == 'R',]
sdata1_all = sdata1
sdata1_all$Condition[sdata1_all$Block == 'R'] = 'R'

#-- Each data point = 1 digit
sdata1w = read.csv(paste(data_dir, 'exp1&2/data_coded_words.csv', sep='/'))
sdata1w = sdata1w[sdata1w$condition %in% c('A', 'B', 'D'),]

#-- Experiment 1
#------------------

compare_conditions(sdata1, 'A', 'B', 'PMissingMorphemes', save.full.model='exp1_morph_AB', models_dir=models_dir)
compare_conditions(sdata1, 'B', 'C', 'PMissingMorphemes', save.full.model='exp1_morph_BC', models_dir=models_dir)
compare_conditions(sdata1, 'C', 'D', 'PMissingMorphemes', save.full.model='exp1_morph_CD', models_dir=models_dir)

compare_conditions(sdata1, 'A', 'B', 'PMissingDigits', save.full.model='exp1_digits_AB', models_dir=models_dir)
compare_conditions(sdata1, 'B', 'C', 'PMissingDigits', save.full.model='exp1_digits_BC', models_dir=models_dir)
compare_conditions(sdata1, 'C', 'D', 'PMissingDigits', save.full.model='exp1_digits_CD', models_dir=models_dir)

compare_conditions(sdata1, 'A', 'B', 'PMissingClasses', save.full.model='exp1_class_AB', models_dir=models_dir)
compare_conditions(sdata1, 'B', 'C', 'PMissingClasses', save.full.model='exp1_class_BC', models_dir=models_dir)
compare_conditions(sdata1, 'C', 'D', 'PMissingClasses', save.full.model='exp1_class_CD', models_dir=models_dir)

compare_conditions(sdata1, 'A', 'B', 'PMissingWords')
compare_conditions(sdata1, 'B', 'C', 'PMissingWords')
compare_conditions(sdata1, 'C', 'D', 'PMissingWords')


#-- Compare 5-digit and 6-digit separately
cat(sprintf('\nAnalysis of 6-digit numbers (%d subjects):\n', length(unique(sdata1$Subject[sdata1$NWordsPerTarget == 7]))))
compare_conditions(sdata1[sdata1$NWordsPerTarget == 7,], 'A', 'B', 'PMissingMorphemes')
compare_conditions(sdata1[sdata1$NWordsPerTarget == 7,], 'B', 'C', 'PMissingMorphemes')
compare_conditions(sdata1[sdata1$NWordsPerTarget == 7,], 'C', 'D', 'PMissingMorphemes')

cat('\nAnalysis of 5-digit numbers:\n')
compare_conditions(sdata1[sdata1$NWordsPerTarget == 6,], 'A', 'B', 'PMissingMorphemes')
compare_conditions(sdata1[sdata1$NWordsPerTarget == 6,], 'B', 'C', 'PMissingMorphemes')
compare_conditions(sdata1[sdata1$NWordsPerTarget == 6,], 'C', 'D', 'PMissingMorphemes')

#-- Interaction between position (hundreds vs. thousands) and condition (A,B vs. D)
pos_cond_interaction(sdata1w)
pos_cond_interaction(sdata1w[sdata1w$condition %in% c('A', 'B'),], target_condition = 'A')

# In condition D, the small difference between the first 2 conditions is not significant:
pos_effect(sdata1w[sdata1w$condition == 'D',], c(1, 2))

#-- Experiment 2
#------------------

#-- Compare conditions
compare_conditions(sdata2, 2, 3, 'PMissingMorphemes')
compare_conditions(sdata2, 3, 4, 'PMissingMorphemes')
compare_conditions(sdata2, 2, 4, 'PMissingMorphemes')
condition_linear_effect(sdata2, 'PMissingMorphemes')

compare_conditions(sdata2, 2, 3, 'PMissingDigits')
compare_conditions(sdata2, 3, 4, 'PMissingDigits')
compare_conditions(sdata2, 2, 4, 'PMissingDigits')
condition_linear_effect(sdata2, 'PMissingDigits')

compare_conditions(sdata2, 2, 3, 'PMissingClasses')
compare_conditions(sdata2, 3, 4, 'PMissingClasses')
compare_conditions(sdata2, 2, 4, 'PMissingClasses')
condition_linear_effect(sdata2, 'PMissingClasses')

compare_conditions(sdata2, 2, 3, 'PMissingWords')
compare_conditions(sdata2, 3, 4, 'PMissingWords')
compare_conditions(sdata2, 2, 4, 'PMissingWords')
condition_linear_effect(sdata2, 'PMissingWords')

#-- Compare D vs. Mixed
compare_conditions(sdata1_all, 'D', 'R', 'PMissingWords', item_intercept = FALSE)


#-- Learning/attention effects? Changes during the block
item_num_effect(sdata1, 'PMissingWords')
item_num_effect(sdata1[sdata1$Condition=='A',], 'PMissingWords')
item_num_effect(sdata1[sdata1$Condition=='B',], 'PMissingWords')
item_num_effect(sdata1[sdata1$Condition=='C',], 'PMissingWords')
item_num_effect(sdata1[sdata1$Condition=='D',], 'PMissingWords')

# first/second half of each block
compare_conditions(sdata1[as.numeric(sdata1$ItemNum) <= 10, ], 'A', 'B', 'PMissingWords')
compare_conditions(sdata1[as.numeric(sdata1$ItemNum) > 10, ], 'A', 'B', 'PMissingWords')

compare_conditions(sdata1[as.numeric(sdata1$ItemNum) <= 10, ], 'C', 'B', 'PMissingWords')
compare_conditions(sdata1[as.numeric(sdata1$ItemNum) > 10, ], 'C', 'B', 'PMissingWords')

compare_conditions(sdata1[as.numeric(sdata1$ItemNum) <= 10, ], 'C', 'D', 'PMissingWords')
compare_conditions(sdata1[as.numeric(sdata1$ItemNum) > 10, ], 'C', 'D', 'PMissingWords')

#--------------------------------------------------------------------------
# Experiment 3
#--------------------------------------------------------------------------

sdata3 = load_data(paste(data_dir, 'exp3/data_coded.csv', sep='/'))

compare_conditions(sdata3, 'A', 'B', 'PMissingMorphemes')
compare_conditions(sdata3, 'A', 'B', 'PMissingDigits')
compare_conditions(sdata3, 'A', 'B', 'PMissingClasses')

#--------------------------------------------------------------------------
# Experiment 4
#--------------------------------------------------------------------------

sdata4 = load_data(paste(data_dir, 'exp4/data_coded.csv', sep='/'))

compare_conditions(sdata4, 'A', 'B', 'PMissingMorphemes')
compare_conditions(sdata4, 'A', 'B', 'PMissingDigits')
compare_conditions(sdata4, 'A', 'B', 'PMissingClasses')

#--------------------------------------------------------------------------
# Experiment 5
#--------------------------------------------------------------------------

sdata5 = load_data(paste(data_dir, 'exp5/data_coded.csv', sep='/'))

compare_conditions(sdata5, 'A', 'B', 'PMissingMorphemes', item_intercept = FALSE)
compare_conditions(sdata5, 'A', 'B', 'PMissingDigits')
compare_conditions(sdata5, 'A', 'B', 'PMissingClasses')
