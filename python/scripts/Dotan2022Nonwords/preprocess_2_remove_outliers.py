import pandas as pd
import mtl.stats as ms

base_dir = '/Users/dror/data/acad-proj/2-InProgress/syntactic chunking nonwords/data/'


df = pd.read_excel(base_dir + 'data_coded.xlsx')


#-- Remove outliers

subj_sum = df.groupby('Subject').mean()

subj_sum[['phonol_error', 'PMissingMorphemes', 'PMissingDigits', 'PMissingClasses']].to_excel(base_dir + 'mean_per_subj.xlsx')

phon_outlier = ms.outlier(subj_sum.phonol_error)
phon_outlier_ids = [sid for sid, o in zip(subj_sum.index, phon_outlier) if o]
print('{} participants are outliers due to phonological errors: {}'.format(sum(phon_outlier), ', '.join(phon_outlier_ids)))

morph_outlier = ms.outlier(subj_sum.PMissingMorphemes)
morph_outlier_ids = [sid for sid, o in zip(subj_sum.index, morph_outlier) if o]
print('{} participants are outliers due to morpheme errors: {}'.format(sum(morph_outlier), ', '.join(morph_outlier_ids)))

outlier_subj_ids = set(phon_outlier_ids + morph_outlier_ids)
df = df[~df.Subject.isin(outlier_subj_ids)]
print('{} outliers were removed, {} participants remained'.format(len(outlier_subj_ids), len(df.Subject.unique())))

df.to_excel(base_dir + 'data_clean.xlsx', index=False)
df.to_csv(base_dir + 'data_clean.csv', index=False)
