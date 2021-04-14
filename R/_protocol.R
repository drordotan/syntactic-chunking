library(lme4)
library(car)
library(zeallot)
library(dplyr)
library(purrr)
library(stringr)
library(effects)
library(gdata)
library(sjPlot)

scripts_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking Nadin/scripts/syntactic-chunking-R'
data_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking Nadin/data'

source(paste(scripts_dir, 'utils.R', sep='/'))
source(paste(scripts_dir, 'sc_basic.R', sep='/'))


#sdata1 = load_data(paste(data_dir, 'exp1/data_coded.csv', sep='/'))
sdata1 = load_data(paste(data_dir, 'exp1/data_exp1.csv', sep='/'), nadin=TRUE, useNErrExcludingOrder = TRUE)
sdata1_blk = sdata1[sdata1$Block != 'R',]
sdata1_mixed = sdata1[sdata1$Block == 'R',]

#--------------------------------------------------------------------------
# Experiment 1
#--------------------------------------------------------------------------

#-- Compare conditions: Blocked

compare_conditions(sdata1_blk, 'A', 'B', 'PMissingWords')
compare_conditions(sdata1_blk, 'B', 'C', 'PMissingWords')
compare_conditions(sdata1_blk, 'C', 'D', 'PMissingWords')

compare_conditions(sdata1_blk, 'A', 'B', 'PMissingDigits')
compare_conditions(sdata1_blk, 'B', 'C', 'PMissingDigits')
compare_conditions(sdata1_blk, 'C', 'D', 'PMissingDigits')

compare_conditions(sdata1_blk, 'A', 'B', 'PMissingClasses')
compare_conditions(sdata1_blk, 'B', 'C', 'PMissingClasses')
compare_conditions(sdata1_blk, 'C', 'D', 'PMissingClasses')

#-- Compare conditions: Mixed
compare_conditions(sdata1_mixed, 2, 3, 'PMissingWords')
compare_conditions(sdata1_mixed, 3, 4, 'PMissingWords')
compare_conditions(sdata1_mixed, 2, 4, 'PMissingWords')

compare_conditions(sdata1_mixed, 2, 3, 'PMissingDigits')
compare_conditions(sdata1_mixed, 3, 4, 'PMissingDigits')
compare_conditions(sdata1_mixed, 2, 4, 'PMissingDigits')

compare_conditions(sdata1_mixed, 2, 3, 'PMissingClasses')
compare_conditions(sdata1_mixed, 3, 4, 'PMissingClasses')
compare_conditions(sdata1_mixed, 2, 4, 'PMissingClasses')


#-- Learning/attention effects? Changes during the block
item_num_effect(sdata1_blk, 'PMissingWords')
item_num_effect(sdata1_blk[sdata1_blk$Condition=='A',], 'PMissingWords')
item_num_effect(sdata1_blk[sdata1_blk$Condition=='B',], 'PMissingWords')
item_num_effect(sdata1_blk[sdata1_blk$Condition=='C',], 'PMissingWords')
item_num_effect(sdata1_blk[sdata1_blk$Condition=='D',], 'PMissingWords')

# first/second half of each block
compare_conditions(sdata1_blk[as.numeric(sdata1_blk$ItemNum) <= 10, ], 'A', 'B', 'PMissingWords')
compare_conditions(sdata1_blk[as.numeric(sdata1_blk$ItemNum) > 10, ], 'A', 'B', 'PMissingWords')

compare_conditions(sdata1_blk[as.numeric(sdata1_blk$ItemNum) <= 10, ], 'C', 'B', 'PMissingWords')
compare_conditions(sdata1_blk[as.numeric(sdata1_blk$ItemNum) > 10, ], 'C', 'B', 'PMissingWords')

compare_conditions(sdata1_blk[as.numeric(sdata1_blk$ItemNum) <= 10, ], 'C', 'D', 'PMissingWords')
compare_conditions(sdata1_blk[as.numeric(sdata1_blk$ItemNum) > 10, ], 'C', 'D', 'PMissingWords')

#--------------------------------------------------------------------------
# Experiment 2
#--------------------------------------------------------------------------

sdata2 = load_data(paste(data_dir, 'exp2/data_exp2.csv', sep='/'), nadin=TRUE)

compare_conditions(sdata2, 'A', 'B', 'PMissingWords')
compare_conditions(sdata2, 'A', 'B', 'PMissingDigits')
compare_conditions(sdata2, 'A', 'B', 'PMissingClasses')

#--------------------------------------------------------------------------
# Experiment 3
#--------------------------------------------------------------------------

sdata3 = load_data(paste(data_dir, 'exp3/data_exp3.csv', sep='/'), nadin=TRUE)
sdata3_item4 = sdata3[sdata3$ItemNum == 4,]

compare_conditions(sdata3, 'A', 'B', 'PMissingWords')
compare_conditions(sdata3, 'A', 'B', 'PMissingDigits')
compare_conditions(sdata3, 'A', 'B', 'PMissingClasses')

compare_conditions_1item(sdata3, 4, 'A', 'B', 'PMissingWords')
compare_conditions_1item(sdata3, 4, 'A', 'B', 'PMissingDigits')
compare_conditions_1item(sdata3, 4, 'A', 'B', 'PMissingClasses')
