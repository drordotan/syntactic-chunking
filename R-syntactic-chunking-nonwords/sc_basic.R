
#--------------------------------------------------------------------------------------------------
load_data <- function(filename, useNErrExcludingOrder=FALSE) {
  sdata = read.csv(filename)
  sdata$ItemNum <- factor(sdata$ItemNum)
  sdata$Subject <- factor(sdata$Subject)
  sdata$NWordsPerTarget = 4
  return(sdata)
}

#--------------------------------------------------------------------------------------------------
compare_conditions <- function(sdata, dependent_var, cond1=NA, cond2=NA, item_intercept=TRUE, save.full.model=NA, models_dir=NA,
                               cond_order_numeric=FALSE, block='order') {
  
  numeric_condition = is.na(cond1)
  
  if (numeric_condition) {
    condition = sdata$Condition
    sdata$Condition = 1
    sdata$Condition[condition == 'B'] = 2
    sdata$Condition[condition == 'C'] = 3
  } else {
    sdata = sdata[sdata$Condition %in% c(cond1, cond2),]
    sdata$cond2 = sdata$Condition %in% cond2

    cond1_order = sdata[, sprintf('order%s', cond1)]
    cond2_order = sdata[, sprintf('order%s', cond2)]
    if (cond_order_numeric) {
      sdata$cond_order = cond2_order - cond1_order
    } else {
      sdata$cond_order = cond1_order < cond2_order
    }
  }
  
  if (is.na(block)) {
    block_factor = ''
  } else if (block == 'order') {
    block_factor = 'cond_order +'
  } else if (block == 'block') {
    block_factor = 'block +'
  } else {
    stop()
  }
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')
  
  sdata$block = factor(sdata$block)
  
  formula1 = sprintf('%s ~ Condition + %s (1|Subject)%s', dependent_var, block_factor, item_intercept_factor)
  formula0 = sprintf('%s ~ %s (1|Subject)%s', dependent_var, block_factor, item_intercept_factor)
  
  print(formula1)
  mdl1 = lmer(as.formula(formula1), data = sdata, REML=FALSE) 
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  
  if (numeric_condition) {
    print_model_coefs(mdl1, '#Condition')
    compare_models(mdl0, mdl1, 'condition')
  } else {
    cond1name = paste(cond1, collapse=",")
    cond2name = paste(cond2, collapse=",")
    compare_models(mdl0, mdl1, sprintf('condition %s (%d items) vs %s  (%d items)', cond1name, sum(!sdata$cond2), cond2name, sum(sdata$cond2)))

    print_model_coefs(mdl1, 'Condition', factor_est_levels=list(Condition=max(cond1, cond2)))
  }
  
  
  if (! is.na(save.full.model)) {
    save_model_coefs(mdl1, save.full.model, models_dir)
  }
}

#--------------------------------------------------------------------------------------------------
block_effect <- function(sdata, dependent_var, item_intercept=TRUE, save.full.model=NA, models_dir=NA) {
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')
  
  sdata$block = as.numeric(sdata$block)
  
  formula.full = sprintf('%s ~ block * Condition + (1|Subject)%s', dependent_var, item_intercept_factor)
  formula.noint = sprintf('%s ~ block + Condition + (1|Subject)%s', dependent_var, item_intercept_factor)
  formula0 = sprintf('%s ~ Condition + (1|Subject)%s', dependent_var, item_intercept_factor)
  
  print(formula.full)
  mdl.full = lmer(as.formula(formula.full), data = sdata, REML=FALSE) 
  mdl.noint = lmer(as.formula(formula.noint), data = sdata, REML=FALSE) 
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  
  print_model_coefs(mdl.full, '#block')
  compare_models(mdl0, mdl.noint, 'block')
  
  compare_models(mdl.noint, mdl.full, 'condition*block interaction')
  
  if (! is.na(save.full.model)) {
    save_model_coefs(mdl1, save.full.model, models_dir)
  }
}

#--------------------------------------------------------------------------------------------------
cond_block_interaction_non_numeric <- function(sdata, dependent_var, item_intercept=TRUE, save.full.model=NA, models_dir=NA) {
  
  sdata$block = factor(sdata$block)
  sdata$Condition = factor(sdata$Condition)
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')

  formula1 = sprintf('%s ~ Condition * block + (1|Subject)%s', dependent_var, item_intercept_factor)
  formula0 = sprintf('%s ~ Condition + block + (1|Subject)%s', dependent_var, item_intercept_factor)
  
  print(formula1)
  mdl1 = lmer(as.formula(formula1), data = sdata, REML=FALSE) 
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  
  compare_models(mdl0, mdl1, 'condition*block interaction')
  
  if (! is.na(save.full.model)) {
    save_model_coefs(mdl1, save.full.model, models_dir)
  }
}


#--------------------------------------------------------------------------------------------------
save_model_coefs <- function(mdl, filename, models_dir) {
  print(sprintf('Saved to %s/%s.html', models_dir, filename))
  tab_model(mdl, file=sprintf('%s/%s.html', models_dir, filename), show.p=FALSE, show.icc=FALSE, show.obs=FALSE, show.ngroups=FALSE)
}
