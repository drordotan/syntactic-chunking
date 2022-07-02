
#dror
#--------------------------------------------------------------------------------------------------
`<-` <- function(a, b) {
  assigning = Sys.getenv("R_IS_ASSIGNING")
  assigning = ifelse(assigning == "" || assigning == "NA", 0, strtoi(assigning))
  assigning = assigning + 1
  Sys.setenv("R_IS_ASSIGNING" = assigning)
  eval.parent(substitute(.Primitive("<-")(a, b)))
  Sys.setenv("R_IS_ASSIGNING" = assigning - 1)
}

is_return_value_assigned <- function() {
  assigning = Sys.getenv("R_IS_ASSIGNING")
  assigning = ifelse(is.na(assigning) || assigning == "", 0, strtoi(assigning))
  return(assigning > 0)
}


#------------------------------------------------------------
# Compare two LMMs 
compare_models <- function(model0, model1, effect_name, trace=FALSE) {
  
  model_diff = anova(model0, model1, test.statistic='LR')
  if (trace) {
    print(model_diff)
  }
  
  likelihood0 = model_diff[1, 4]
  likelihood1 = model_diff[2, 4]
  
  if (likelihood1 < likelihood0) {
    
    cat(sprintf('>>> Effect of %s: strange, the model without the additional factor was better\n', effect_name))
    print(model_diff)
    
  } else if (likelihood1 == likelihood0) {
    
    cat(sprintf('>>> No effect of %s: removing the factor did not change the model\'s likelihood\n', effect_name))
    
  } else {
    chi2 = model_diff[2,6]
    chi2df = model_diff[2,7]
    p = model_diff[2,8]
    
    cat(sprintf('>>> Effect of %s: chi2(%d)=%.2f, p=%s\n', effect_name, chi2df, chi2, p_str(p)))
  }
  
  if (trace) {
    print('')
  }
  
  if (is_return_value_assigned()) {
    return(p)
  }
}


#--------------------------------------------------------------------------------------------------
printable_mode_formula <- function(mdl) {
  formula_parts = strsplit(deparse(mdl@call$formula), "~")
  dependent_var = get_pred_desc(formula_parts[[1]][1])
  predictors = strsplit(formula_parts[[1]][2], "[+]")[[1]]

  result = dependent_var
  delimiter = " ~ "
  for (pd in predictors) {
    result = paste(result, get_pred_desc(pd), sep=delimiter)
    delimiter = " + "
  }
  return(result)
}

#--------------------------------------------------------------------------------------------------
save_model_coefs <- function(mdl, filename) {
  tab_model(mdl, file = filename, show.p = FALSE, show.icc = FALSE, show.obs = FALSE, show.ngroups = FALSE)
}

#--------------------------------------------------------------------------------------------------
# Print the model's coefficients
#
# factor_names: a vector of factor names. Each factor name may be preceded by '@', to indicate it's a boolean factor (TRUE/FALSE).
#               
#
print_model_coefs <- function(mdl, factor_names, factor_est_levels=list(), print_full=FALSE) {
  
  sm = summary(mdl)
  sig = Anova(mdl)
  
  if (print_full) {
    print('Model coefficients:')
    print(sm$coefficients[,1])
  }
  
  coeff_precision = 3

  result = c()
  for (factor in factor_names) {
    
    factor_type = substr(factor, 1, 1)
    if (factor_type == '@') {
      factor = substr(factor, 2, 99999)
      est_name = paste(factor, 'TRUE', sep='')
      desc = paste(factor, '=TRUE', sep='')
    } else if (factor_type == '#') {
      factor = substr(factor, 2, 99999)
      desc = factor
      est_name = factor
    } else {
      c(est_name, desc) %<-% add_level(factor, factor_est_levels)
    }
    
    if (! (est_name %in% row.names(sm$coefficients))) {
      print(sm)
      stop(sprintf('Factor "%s" not found in model summary', est_name))
    }
    if (desc == '') {
      coeff_suffix = ''
    } else {
      coeff_suffix = sprintf(' (for %s)', desc)
    }
    
    coeff_value = sm$coefficients[est_name, 'Estimate']
    coeff_sd = sm$coefficients[est_name, 'Std. Error']
    
    result = c(result, coeff_value)
    
    part1 = sprintf('LMM factor %s%s: coeff = %.*f, SE = %.*f, OddsRatio = %.2f', factor, coeff_suffix,
                    coeff_precision, coeff_value, coeff_precision, coeff_sd, exp(coeff_value))
    
    #-- This is for printing significance. Usually we don't need it - we compute significance using another method.
    #part2 = sprintf('; chi2(%d) = %.2f, p=%s', sig[factor, 'Df'], sig[factor, 'Chisq'], p_str(sig[factor, 'Pr(>Chisq)'])) 
    part2 = ''
    
    cat(part1)
    cat('\n')
  }
  
  if (is_return_value_assigned()) {
    return(result)
  }
}


#-------------------------------------------------------------------
# Convert a list of factors ("factor1:factor2" string) to the same factors with levels: "factor1A:factor2B", where A and B are the levels defined for factors 1 and 2
# If a factor does not have a level, don't add it
add_level <- function(factor, factor_est_levels) {
  
  factors = strsplit(factor, ':')[[1]]
  
  factor_with_level = c()
  desc = c()
  
  for (f in factors) {
    
    if (f %in% names(factor_est_levels)) {
      factor_and_level = paste(f, factor_est_levels[f], sep='')
      desc = c(desc, sprintf('%s=%s', f, factor_est_levels[f]))
    } else {
      factor_and_level = f
    }
    
    factor_with_level = c(factor_with_level, factor_and_level)
  }
  
  factor_with_level = paste(factor_with_level, collapse=':')
  desc = paste(desc, collapse=', ')
  
  return (c(factor_with_level, desc))
}


#--------------------------------------------------------------------------------------------------
# Weight the data in inverse proportion to the subject's number of samples
# 
get_weights_by_subject_nsamples <- function(data) {
  
  nnn = summarise(group_by(data, subject), n())
  subj_id = nnn$subject
  n_samples_subject = nnn[[2]]
  
  result = rep(NA, nrow(data))
  for (i in 1:length(subj_id)) {
    subj = subj_id[i]
    subj_n = n_samples_subject[i]
    result[data$subject == subj] = mean(n_samples_subject) / subj_n
  }
  return(result)
}


#--------------------------------------------------------------------------------------------------
# Get the string description of factors.
# Each factor is added only if the data contains more than one value for this factor

get_factors_for_multiple_values = function(factor_names, data) {
  factors_str = ''
  for (factor in factor_names) {
    if (length(unique(data[,factor])) > 1) {
      factors_str = paste(c(factors_str, factor, ' + '), sep='', collapse = '')
    }
  }
  return(factors_str)
}


#--------------------------------------------------------------------------------------------------
p_str <- function(p) {
  
  if (p == 0) {
    return('0')
  } else if (p > .15) {
    return(sprintf("%.03f", p))
  } else if (p > .001) {
    return(sprintf("%.04f", p))
  } else if (p > .0001) {
    return(sprintf("%.05f", p))
  } else {
    return(sprintf("1e%d", ceiling(log(p) / log(10))))
  }
}
