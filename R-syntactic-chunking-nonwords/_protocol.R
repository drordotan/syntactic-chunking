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

scripts_dir = '/Users/dror/git/syntactic-chunking/R-syntactic-chunking-nonwords'
data_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/data'
models_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/figures/models'

source(paste(scripts_dir, 'utils.R', sep='/'))
source(paste(scripts_dir, 'sc_basic.R', sep='/'))

Sys.setenv("R_IS_ASSIGNING" = 0)

#--------------------------------------------------------------------------

sdata = load_data(paste(data_dir, 'data_clean.csv', sep='/'))

#-- Pre-registered analyses

compare_conditions(sdata, 'PMissingMorphemes','A', 'B', save.full.model='exp1_morph_AB', models_dir=models_dir)
compare_conditions(sdata, 'PMissingMorphemes','B', 'C', save.full.model='exp1_morph_BC', models_dir=models_dir)

compare_conditions(sdata, 'PMissingDigits', 'A', 'B', save.full.model='exp1_digits_AB', models_dir=models_dir)
compare_conditions(sdata, 'PMissingDigits', 'B', 'C', save.full.model='exp1_digits_BC', models_dir=models_dir)

compare_conditions(sdata, 'PMissingClasses', 'A', 'B', save.full.model='exp1_class_AB', models_dir=models_dir)
compare_conditions(sdata, 'PMissingClasses', 'B', 'C', save.full.model='exp1_class_BC', models_dir=models_dir)


#-- Effect of learning from block to block

block_effect(sdata, 'PMissingMorphemes')
block_effect(sdata[sdata$Condition == 'A',], 'PMissingMorphemes')
block_effect(sdata[sdata$Condition == 'B',], 'PMissingMorphemes')
block_effect(sdata[sdata$Condition == 'C',], 'PMissingMorphemes')

#-- Effect of learning inside the first block
sdata$quartile = floor(as.numeric(sdata$ItemNum) / 4) + 1
for (block in 1:3) {
  cat('\n')
  print(sprintf('Block %d', block))
  block_effect(sdata[sdata$block == block & sdata$Condition == 'A',], 'PMissingMorphemes', block_field = 'quartile', header_lin=sprintf('Block %d, condition A', block))
  block_effect(sdata[sdata$block == block & sdata$Condition == 'B',], 'PMissingMorphemes', block_field = 'quartile', header_lin=sprintf('Block %d, condition B', block))
  block_effect(sdata[sdata$block == block & sdata$Condition == 'C',], 'PMissingMorphemes', block_field = 'quartile', header_lin=sprintf('Block %d, condition C', block))
  block_effect(sdata[sdata$block == block,], 'PMissingMorphemes', block_field = 'quartile', header_lin=sprintf('Block %d, all conditions', block))
}

