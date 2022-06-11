
library(simr)

power_analysis_exp1 <- function(sdata, cond1, cond2, nsubjects=35) {
  
  print(sprintf('\n\n======================== %s Versus %s', cond1, cond2))
  fit <- lmer(PMissingMorphemes ~ Condition + (1|Subject), data=sdata[sdata$Condition %in% c(cond1, cond2),])
  if (! is.na(nsubjects)) {
    fit <- extend(fit, along="Subject", n=nsubjects)
  }
  powerSim(fit, nsim = 200)
}


power_analysis_numeric_cond <- function(sdata, nsubjects=NA) {
  
  sdata$Condition = as.numeric(sdata$Condition)
  fit <- lmer(PMissingMorphemes ~ Condition + (1|Subject), data=sdata)
  if (! is.na(nsubjects)) {
    fit <- extend(fit, along="Subject", n=nsubjects)
  }
  
  powerSim(fit, nsim = 200)
}

power_analysis_2cond <- function(sdata, nsubjects=NA) {
  fit <- lmer(PMissingMorphemes ~ Condition + (1|Subject), data=sdata)
  if (! is.na(nsubjects)) {
    fit <- extend(fit, along="Subject", n=nsubjects)
  }
  powerSim(fit, nsim = 200)
}


power_analysis_exp1(sdata1, 'A', 'B')
power_analysis_exp1(sdata1, 'A', 'B', nsubjects=35)
power_analysis_exp1(sdata1, 'B', 'C')
power_analysis_exp1(sdata1, 'C', 'D')

power_analysis_numeric_cond(sdata2)
power_analysis_numeric_cond(sdata2, nsubjects=35)

power_analysis_2cond(sdata3)
power_analysis_2cond(sdata4)
power_analysis_2cond(sdata5)
