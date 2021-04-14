
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
compare_conditions <- function(sdata, cond1, cond2, dependent_var, item_intercept=TRUE) {
  
  sdata = sdata[sdata$Condition %in% c(cond1, cond2),]
  sdata$cond2 = sdata$Condition %in% cond2
  
  item_intercept_factor = ifelse(item_intercept, ' + (1|ItemNum)', '')
  
  formula1 = sprintf('%s ~ cond2 + (1|Subject)%s', dependent_var, item_intercept_factor)
  formula0 = sprintf('%s ~ (1|Subject)%s', dependent_var, item_intercept_factor)
  
  mdl1 = lmer(as.formula(formula1), data = sdata, REML=FALSE) 
  mdl0 = lmer(as.formula(formula0), data = sdata, REML=FALSE) 
  
  cond1name = paste(cond1, collapse=",")
  cond2name = paste(cond2, collapse=",")
  compare_models(mdl0, mdl1, sprintf('condition %s (%d items) vs %s  (%d items)', cond1name, sum(!sdata$cond2), cond2name, sum(sdata$cond2)))
  
  print_model_coefs(mdl1, '@cond2')
}

#--------------------------------------------------------------------------------------------------
compare_conditions_1item <- function(sdata, item_num, cond1, cond2, dependent_var) {
  
  sdata = sdata[sdata$Condition %in% c(cond1, cond2) & sdata$ItemNum == item_num,]
  sdata = sdata[order(sdata$Subject),]
  
  data.cond1 = sdata[sdata$Condition == cond1, dependent_var]
  data.cond2 = sdata[sdata$Condition == cond2, dependent_var]
  
  w.res = wilcox.test(data.cond1, data.cond2, paired = TRUE)
  print(sprintf('Comparing %s between conditions %s vs. %s in item #%d: V=%g, 1-tailed p=%s (%s)', 
                dependent_var, cond1, cond2, item_num, w.res$statistic, p_str(w.res$p.value / 2), w.res$method))
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
