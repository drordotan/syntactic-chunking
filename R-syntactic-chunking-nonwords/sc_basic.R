
#--------------------------------------------------------------------------------------------------
load_data <- function(filename, useNErrExcludingOrder=FALSE) {
  sdata = read.csv(filename)
  sdata$ItemNum <- factor(sdata$ItemNum)
  sdata$Subject <- factor(sdata$Subject)
  sdata$NWordsPerTarget = 4
  return(sdata)
}

#--------------------------------------------------------------------------------------------------
compare_conditions <- function(sdata, dependent_var, cond1=NA, cond2=NA, item_intercept=TRUE, save.full.model=NA, models_dir=NA) {
  
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
    sdata$cond_order = cond1_order < cond2_order
  }
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')
  
  formula1 = sprintf('%s ~ Condition + cond_order + (1|Subject)%s', dependent_var, item_intercept_factor)
  formula0 = sprintf('%s ~ cond_order + (1|Subject)%s', dependent_var, item_intercept_factor)
  
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
  
  #r2.1 = r.squaredGLMM(mdl1)[1]
  #r2.0 = r.squaredGLMM(mdl0)[1]
  #effect_size = (r2.1 - r2.0) / (1 - r2.1)
  #print(sprintf('Effect size: %.3f', effect_size))
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


#--------------------------------------------------------------------------------------------------
#-- Interaction between position (hundreds vs. thousands) and condition (A,B vs. D)
pos_cond_interaction <- function(sdata, target_condition='D') {
  
  sdata = sdata[!is.na(sdata$digit_ok) & sdata$n_target_words == 6,]
  sdata$condD = sdata$condition == target_condition
  
  sdata$position = NA
  
  for (cond in unique(sdata$condition)) {
    word_orders = sort(unique(sdata$word_order[sdata$condition == cond]))
    sdata$position[sdata$condition == cond] <- mapvalues(sdata$word_order[sdata$condition == cond], from=word_orders, to=1:length(word_orders))
  }
  
  sdata <- sdata[sdata$position %in% c(2,3),]
  
  mdl1 = glmer(digit_ok ~ condD * position + (1|item_num) + (1|subject), data=sdata, family=binomial)
  mdl0 = glmer(digit_ok ~ condD + position + (1|item_num) + (1|subject), data=sdata, family=binomial)

  compare_models(mdl0, mdl1, 'condition-position interaction')
  print_model_coefs(mdl1, 'condDTRUE:position')
}

#--------------------------------------------------------------------------------------------------
#-- Effect of position in one conditions
pos_effect <- function(sdata, positions) {
  
  sdata = sdata[!is.na(sdata$digit_ok) & sdata$n_target_words == 6,]

  sdata$position = NA
  
  word_orders = sort(unique(sdata$word_order))
  sdata$position <- mapvalues(sdata$word_order, from=word_orders, to=1:length(word_orders))
  
  sdata <- sdata[sdata$position %in% positions,]
  
  mdl1 = glmer(digit_ok ~ position + (1|item_num) + (1|subject), data=sdata, family=binomial)
  mdl0 = glmer(digit_ok ~ (1|item_num) + (1|subject), data=sdata, family=binomial)
  
  compare_models(mdl0, mdl1, 'position')
  print_model_coefs(mdl1, 'position')
}


#--------------------------------------------------------------------------------------------------
save_model_coefs <- function(mdl, filename, models_dir) {
  print(sprintf('Saved to %s/%s.html', models_dir, filename))
  tab_model(mdl, file=sprintf('%s/%s.html', models_dir, filename), show.p=FALSE, show.icc=FALSE, show.obs=FALSE, show.ngroups=FALSE)
}
