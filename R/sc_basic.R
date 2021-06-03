
#--------------------------------------------------------------------------------------------------
load_data <- function(filename, nadin=FALSE, useNErrExcludingOrder=FALSE) {
  sdata = read.csv(filename)
  
  if (nadin) {
    
    if (useNErrExcludingOrder) {
      sdata$NMissingWords = sdata$NErrExcludingOrder
    }
    
    for (colname in c('NMissingWords', 'NMissingDigits', 'NMissingClasses')) {
      sdata[is.na(sdata[, colname]), colname] = 0
    }
    
    sdata$PMissingWords = sdata$NMissingWords / sdata$NWordsPerTarget
    sdata$PMissingDigits = sdata$NMissingDigits / sdata$NWordsPerTarget
    sdata$PMissingClasses = sdata$NMissingClasses / sdata$NWordsPerTarget
  }
  
  sdata$ItemNum <- factor(sdata$ItemNum)
  return(sdata)
}

#--------------------------------------------------------------------------------------------------
load_morphemes <- function(filename) {
  df_words = read.csv(filename)
  
  result = df_words
  result$morphemeOK = result$digitOK
  result$morphemeType = 'digit'

  result2 = df_words
  result2$morphemeOK = result2$classOK
  result2$morphemeType = 'class'
  
  return (rbind(result, result2))
}

#--------------------------------------------------------------------------------------------------
compare_conditions <- function(sdata, cond1, cond2, dependent_var, item_intercept=TRUE, logistic=FALSE) {
  
  sdata = sdata[sdata$Condition %in% c(cond1, cond2),]
  sdata$cond2 = sdata$Condition %in% cond2
  
  if (logistic) {
    sdata = repeat_rows(sdata, 'NWordsPerTarget')
  }
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')
  
  formula1 = sprintf('%s ~ cond2 + (1|Subject)%s', dependent_var, item_intercept_factor)
  formula0 = sprintf('%s ~ (1|Subject)%s', dependent_var, item_intercept_factor)
  
  if (logistic) {
    mdl1 = glmer(as.formula(formula1), data = sdata, family=binomial) 
    mdl0 = glmer(as.formula(formula0), data = sdata, family=binomial) 
  } else {
    mdl1 = lmer(as.formula(formula1), data = sdata, REML=FALSE) 
    mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  }
  
  cond1name = paste(cond1, collapse=",")
  cond2name = paste(cond2, collapse=",")
  compare_models(mdl0, mdl1, sprintf('condition %s (%d items) vs %s  (%d items)', cond1name, sum(!sdata$cond2), cond2name, sum(sdata$cond2)))
  
  print_model_coefs(mdl1, '@cond2')
}

#--------------------------------------------------------------------------------------------------
compare_conditions_w <- function(sdata, cond1, cond2, dependent_var, item_intercept=TRUE) {
  
  sdata = sdata[sdata$condition %in% c(cond1, cond2),]
  sdata$cond2 = sdata$condition %in% cond2
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|itemNum)', '')
  
  formula1 = sprintf('%s ~ cond2 + nTargetWords + (1|subject)%s', dependent_var, item_intercept_factor)
  formula0 = sprintf('%s ~ nTargetWords + (1|subject)%s', dependent_var, item_intercept_factor)
  
  mdl1 = glmer(as.formula(formula1), data = sdata, family=binomial)
  mdl0 = glmer(as.formula(formula0), data = sdata, family=binomial)
  
  cond1name = paste(cond1, collapse=",")
  cond2name = paste(cond2, collapse=",")
  compare_models(mdl0, mdl1, sprintf('condition %s (%d items) vs %s  (%d items)', cond1name, sum(!sdata$cond2), cond2name, sum(sdata$cond2)))
  
  print_model_coefs(mdl1, '@cond2')
}

#--------------------------------------------------------------------------------------------------
# Morphological comparison
compare_conditions_morphemes <- function(sdata, cond1, cond2, morpheme_type=NA, item_intercept=TRUE) {
  
  sdata = sdata[sdata$condition %in% c(cond1, cond2),]
  sdata$cond2 = sdata$condition %in% cond2
  
  if (is.na(morpheme_type)) {
    target_length_factor = 'nTargetMorphemes'
    morpheme_type_factor = 'morpheme_type + '
  } else if (morpheme_type == 'digit') {
    target_length_factor = 'nTargetDigits'
    morpheme_type_factor = ''
    sdata = sdata[sdata$morpheme_type==morpheme_type,]
  } else if (morpheme_type == 'class') {
    target_length_factor = 'nTargetWords'
    morpheme_type_factor = ''
    sdata = sdata[sdata$morpheme_type==morpheme_type,]
  } else {
    stop('Invalid morpheme type')
  }
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|itemNum)', '')
  
  formula1 = sprintf('correct ~ cond2 + %s + %s(1|subject)%s', target_length_factor, morpheme_type_factor, item_intercept_factor)
  formula0 = sprintf('correct ~ %s + %s(1|subject)%s', target_length_factor, morpheme_type_factor, item_intercept_factor)
  
  mdl1 = glmer(as.formula(formula1), data = sdata, family=binomial)
  mdl0 = glmer(as.formula(formula0), data = sdata, family=binomial)
  
  cond1name = paste(cond1, collapse=",")
  cond2name = paste(cond2, collapse=",")
  compare_models(mdl0, mdl1, sprintf('condition %s (%d items) vs %s  (%d items)', cond1name, sum(!sdata$cond2), cond2name, sum(sdata$cond2)))
  
  print_model_coefs(mdl1, '@cond2')
}


#--------------------------------------------------------------------------------------------------
# Subject-level analysis (run for all subjects)
compare_conditions_per_subj <- function(sdata, cond1, cond2, dependent_var, alpha=0.05) {
  
  subj_ids = unique(sdata$Subject)
  all_p = c()
  for (subj_id in subj_ids) {
    p = compare_conditions_1subj(sdata, subj_id, cond1, cond2, dependent_var)
    all_p = c(all_p, p)
  }
  
  nsubj = length(all_p)
  
  inds = order(all_p)
  all_p = all_p[inds]
  subj_ids = subj_ids[inds]
  
  nonsignificant_subj_ids = c()
  
  n_significant = 0
  for (i in seq_len(nsubj)) {
    threshold = alpha / (nsubj + 1 - i)
    if (all_p[i] <= threshold) {
      n_significant = n_significant + 1
    } else {
      nonsignificant_subj_ids = c(nonsignificant_subj_ids, subj_ids[i])
    }
  }
  cat('\n')
  cat(sprintf('%d/%d subjects had a significant syntactic chunking effect\n', n_significant, nsubj))
  cat(sprintf('Non-significant subjects: %s\n', paste(nonsignificant_subj_ids, collapse = ',')))
  #print('P values:')
  #print(sprintf('%.6f', all_p))
}

#---------------------------------------------------
compare_conditions_1subj <- function(sdata, subj_id, cond1, cond2, dependent_var) {
  
  sdata = sdata[sdata$Subject == subj_id,]
  sdata = sdata[sdata$Condition %in% c(cond1, cond2),]
  sdata$cond2 = sdata$Condition %in% cond2
  initial_coeff = mean(sdata[sdata$cond2, dependent_var])- mean(sdata[!sdata$cond2, dependent_var])
  
  formula1 = sprintf('%s ~ cond2 + (1|ItemNum)', dependent_var)
  formula0 = sprintf('%s ~ (1|ItemNum)', dependent_var)
  
  estimated_coeff_value = mean(sdata[sdata$cond2, dependent_var]) - mean(sdata[!sdata$cond2, dependent_var])
  
  mdl1 = lmer(as.formula(formula1), data = sdata, REML=FALSE, start=c(cond2=estimated_coeff_value))
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE)
  
  cond1name = paste(cond1, collapse=",")
  cond2name = paste(cond2, collapse=",")
  p <- compare_models(mdl0, mdl1, sprintf('Subject %s: condition %s (%d items) vs %s  (%d items)', subj_id, cond1name, sum(!sdata$cond2), cond2name, sum(sdata$cond2)))
  
  print_model_coefs(mdl1, '@cond2')
  
  return(p)
}

#--------------------------------------------------------------------------------------------------
condition_linear_effect <- function(sdata, dependent_var, item_intercept=FALSE) {
  
  sdata$Condition = as.numeric(sdata$Condition)
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')
  
  formula1 = sprintf('%s ~ Condition + (1|Subject)%s', dependent_var, item_intercept_factor)
  formula0 = sprintf('%s ~ (1|Subject)%s', dependent_var, item_intercept_factor)
  
  mdl1 = lmer(as.formula(formula1), data = sdata, REML=FALSE) 
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  
  compare_models(mdl0, mdl1, 'condition (numeric)')
  
  print_model_coefs(mdl1, 'Condition')
}

#--------------------------------------------------------------------------------------------------
item_num_effect <- function(sdata, dependent_var) {
  
  sdata$ItemNum = as.numeric(sdata$ItemNum)
  
  n_conds = length(unique(sdata$Condition))
  if (n_conds > 1) {
    formula1 = sprintf('%s ~ Condition * ItemNum + (1|Subject)', dependent_var)
    formula0 = sprintf('%s ~ Condition + (1|Subject)', dependent_var)
  } else {
    formula1 = sprintf('%s ~ ItemNum + (1|Subject)', dependent_var)
    formula0 = sprintf('%s ~ (1|Subject)', dependent_var)
  }
  
  mdl1 = lmer(as.formula(formula1), data = sdata, REML=FALSE) 
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  
  compare_models(mdl0, mdl1, 'item-number')
  
  print_model_coefs(mdl1, '#ItemNum')
}
