
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
                               cond_order_numeric=FALSE, block='order', print_means=FALSE) {
  
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
  
  if (print_means) {
    print(sprintf('Condition %s %s = %.2f%%', cond1, dependent_var, mean(sdata[sdata$Condition == cond1, dependent_var]) * 100))
    print(sprintf('Condition %s %s = %.2f%%', cond2, dependent_var, mean(sdata[sdata$Condition == cond2, dependent_var]) * 100))
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
block_effect <- function(sdata, dependent_var, item_intercept=TRUE, save.full.model=NA, models_dir=NA, block_as_numeric_factor=TRUE,
                         block_field='block', header_line=NA) {
  
  if (! is.na(header_line)) {
    print(header_line)
  }
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')
  
  if (block_as_numeric_factor) {
    sdata[block_field] = as.numeric(sdata[,block_field])
  } else {
    sdata[block_field] = factor(sdata[,block_field])
  }
  multiple_conditions = length(unique(sdata$Condition)) > 1
  
  cond_factor = ifelse(multiple_conditions, 'Condition + ', '')
  formula.noint = sprintf('%s ~ %s + %s(1|Subject)%s', dependent_var, block_field, cond_factor, item_intercept_factor)
  formula0 = sprintf('%s ~ %s(1|Subject)%s', dependent_var, cond_factor, item_intercept_factor)
  
  print(formula.noint)
  mdl.noint = lmer(as.formula(formula.noint), data = sdata, REML=FALSE) 
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  
  if (block_as_numeric_factor) {
    print_model_coefs(mdl.noint, sprintf('#%s', block_field))
  }
  compare_models(mdl0, mdl.noint, block_field)
  
  if (multiple_conditions) {
    formula.full = sprintf('%s ~ %s * Condition + (1|Subject)%s', dependent_var, block_field, item_intercept_factor)
    mdl.full = lmer(as.formula(formula.full), data = sdata, REML=FALSE) 
    compare_models(mdl.noint, mdl.full, sprintf('condition*%s interaction', block_field))
  }
  
  if (! is.na(save.full.model)) {
    save_model_coefs(mdl1, save.full.model, models_dir)
  }
}

#--------------------------------------------------------------------------------------------------
in_block_learning_effect <- function(sdata, dependent_var, item_intercept=TRUE, save.full.model=NA, models_dir=NA, block_as_numeric_factor=TRUE) {
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')
  
  if (block_as_numeric_factor) {
    sdata$block = as.numeric(sdata$block)
  } else {
    sdata$block = factor(sdata$block)
  }
  multiple_conditions = length(unique(sdata$Condition)) > 1
  
  cond_factor = ifelse(multiple_conditions, 'Condition + ', '')
  formula.noint = sprintf('%s ~ block + %s(1|Subject)%s', dependent_var, cond_factor, item_intercept_factor)
  formula0 = sprintf('%s ~ %s(1|Subject)%s', dependent_var, cond_factor, item_intercept_factor)
  
  print(formula.noint)
  mdl.noint = lmer(as.formula(formula.noint), data = sdata, REML=FALSE) 
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  
  if (block_as_numeric_factor) {
    print_model_coefs(mdl.noint, '#block')
  }
  compare_models(mdl0, mdl.noint, 'block')
  
  if (multiple_conditions) {
    formula.full = sprintf('%s ~ block * Condition + (1|Subject)%s', dependent_var, item_intercept_factor)
    mdl.full = lmer(as.formula(formula.full), data = sdata, REML=FALSE) 
    compare_models(mdl.noint, mdl.full, 'condition*block interaction')
  }
  
  if (! is.na(save.full.model)) {
    save_model_coefs(mdl1, save.full.model, models_dir)
  }
}

#--------------------------------------------------------------------------------------------------
save_model_coefs <- function(mdl, filename, models_dir) {
  print(sprintf('Saved to %s/%s.html', models_dir, filename))
  tab_model(mdl, file=sprintf('%s/%s.html', models_dir, filename), show.p=FALSE, show.icc=FALSE, show.obs=FALSE, show.ngroups=FALSE)
}
