1. Run the script and generate GTEx_GENE_WEIGHTS.txt

./gene_reads_to_GTEx_GENE_WEIGHTS.pl > GTEx_GENE_WEIGHTS.2.txt

#HOW TO NORMALIZE THE DATA (hardcoded inside the script)
#1 -> log10($_+1)/$log10maxMedianPlusOne;
#2 -> by median across the tissues
#3 -> by mean across the tissues
#4 -> to Z-score
#any other -> do not normalize

2. Create table in MySQL

Create table GTEx_GENE_WEIGHTS(GEN_ID varchar(255), GENE varchar(255), Adipose_Subcutaneous double, Adipose_Visceral_Omentum double, Adrenal_Gland double, Artery_Aorta double, Artery_Coronary double, Artery_Tibial double, Bladder double, Brain_Amygdala double, Brain_Anterior_cingulate_cortex_BA24 double, Brain_Caudate_basal_ganglia double, Brain_Cerebellar_Hemisphere double, Brain_Cerebellum double, Brain_Cortex double, Brain_Frontal_Cortex_BA9 double, Brain_Hippocampus double, Brain_Hypothalamus double, Brain_Nucleus_accumbens_basal_ganglia double, Brain_Putamen_basal_ganglia double, Brain_Spinal_cord_cervical_c_1 double, Brain_Substantia_nigra double, Breast_Mammary_Tissue double, Cells_EBV_transformed_lymphocytes double, Cells_Transformed_fibroblasts double, Cervix_Ectocervix double, Cervix_Endocervix double, Colon_Sigmoid double, Colon_Transverse double, Esophagus_Gastroesophageal_Junction double, Esophagus_Mucosa double, Esophagus_Muscularis double, Fallopian_Tube double, Heart_Atrial_Appendage double, Heart_Left_Ventricle double, Kidney_Cortex double, Liver double, Lung double, Minor_Salivary_Gland double, Muscle_Skeletal double, Nerve_Tibial double, Ovary double, Pancreas double, Pituitary double, Prostate double, Skin_Not_Sun_Exposed_Suprapubic double, Skin_Sun_Exposed_Lower_leg double, Small_Intestine_Terminal_Ileum double, Spleen double, Stomach double, Testis double, Thyroid double, Uterus double, Vagina double, Whole_Blood double);


3. Load data to the table

mysqlimport --local --host=dev-clone-july22.cxrzznxifeib.us-east-1.rds.amazonaws.com --user=diguser --password=type2diabetes digkb GTEx_GENE_WEIGHTS.txt


4. Index all columns

ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX GEN_ID_IDX(GEN_ID(255));
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX GENE_IDX(GENE(255));
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Adipose_Subcutaneous_IDX(Adipose_Subcutaneous);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Adipose_Visceral_Omentum_IDX(Adipose_Visceral_Omentum);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Adrenal_Gland_IDX(Adrenal_Gland);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Artery_Aorta_IDX(Artery_Aorta);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Artery_Coronary_IDX(Artery_Coronary);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Artery_Tibial_IDX(Artery_Tibial);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Bladder_IDX(Bladder);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Amygdala_IDX(Brain_Amygdala);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Anterior_cingulate_cortex_BA24_IDX(Brain_Anterior_cingulate_cortex_BA24);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Caudate_basal_ganglia_IDX(Brain_Caudate_basal_ganglia);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Cerebellar_Hemisphere_IDX(Brain_Cerebellar_Hemisphere);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Cerebellum_IDX(Brain_Cerebellum);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Cortex_IDX(Brain_Cortex);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Frontal_Cortex_BA9_IDX(Brain_Frontal_Cortex_BA9);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Hippocampus_IDX(Brain_Hippocampus);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Hypothalamus_IDX(Brain_Hypothalamus);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Nucleus_accumbens_basal_ganglia_IDX(Brain_Nucleus_accumbens_basal_ganglia);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Putamen_basal_ganglia_IDX(Brain_Putamen_basal_ganglia);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Spinal_cord_cervical_c_1_IDX(Brain_Spinal_cord_cervical_c_1);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Brain_Substantia_nigra_IDX(Brain_Substantia_nigra);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Breast_Mammary_Tissue_IDX(Breast_Mammary_Tissue);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Cells_EBV_transformed_lymphocytes_IDX(Cells_EBV_transformed_lymphocytes);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Cells_Transformed_fibroblasts_IDX(Cells_Transformed_fibroblasts);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Cervix_Ectocervix_IDX(Cervix_Ectocervix);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Cervix_Endocervix_IDX(Cervix_Endocervix);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Colon_Sigmoid_IDX(Colon_Sigmoid);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Colon_Transverse_IDX(Colon_Transverse);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Esophagus_Gastroesophageal_Junction_IDX(Esophagus_Gastroesophageal_Junction);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Esophagus_Mucosa_IDX(Esophagus_Mucosa);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Esophagus_Muscularis_IDX(Esophagus_Muscularis);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Fallopian_Tube_IDX(Fallopian_Tube);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Heart_Atrial_Appendage_IDX(Heart_Atrial_Appendage);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Heart_Left_Ventricle_IDX(Heart_Left_Ventricle);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Kidney_Cortex_IDX(Kidney_Cortex);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Liver_IDX(Liver);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Lung_IDX(Lung);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Minor_Salivary_Gland_IDX(Minor_Salivary_Gland);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Muscle_Skeletal_IDX(Muscle_Skeletal);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Nerve_Tibial_IDX(Nerve_Tibial);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Ovary_IDX(Ovary);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Pancreas_IDX(Pancreas);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Pituitary_IDX(Pituitary);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Prostate_IDX(Prostate);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Skin_Not_Sun_Exposed_Suprapubic_IDX(Skin_Not_Sun_Exposed_Suprapubic);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Skin_Sun_Exposed_Lower_leg_IDX(Skin_Sun_Exposed_Lower_leg);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Small_Intestine_Terminal_Ileum_IDX(Small_Intestine_Terminal_Ileum);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Spleen_IDX(Spleen);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Stomach_IDX(Stomach);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Testis_IDX(Testis);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Thyroid_IDX(Thyroid);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Uterus_IDX(Uterus);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Vagina_IDX(Vagina);
ALTER TABLE GTEx_GENE_WEIGHTS ADD INDEX Whole_Blood_IDX(Whole_Blood);
