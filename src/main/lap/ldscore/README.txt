				________

				 README

				 tgreen
				________


Table of Contents
_________________

1 Description
2 Munge stats
.. 2.1 sumstats_in
.. 2.2 snp_list
.. 2.3 munge_results
3 LDscore regression
.. 3.1 Reformatting Description
.. 3.2 File types:
..... 3.2.1 File 1.  .annot.gz* reformat
..... 3.2.2 File 2. baseline.1.l2.M*
..... 3.2.3 File 3. baseline.1.l2.M_5_50*
..... 3.2.4 File 4. ldscore.gz*
.. 3.3 Command
.. 3.4 Run
4 Load


1 Description
=============

  Pipeline to get cell-type specific LD score regression statistics.
  with multiple steps.

  Software can be downloaded from

  [https://github.com/bulik/ldsc]

  Information about data to download can be found at

  [https://github.com/bulik/ldsc/wiki/Cell-type-specific-analyses]


2 Munge stats
=============

  python /humgen/diabetes/users/tgreen/software/ldsc/munge_sumstats.py

  --sumstats <sumstats_in>

  --merge-alleles <snp_list>

  --out <munge_result>

  The data input for these steps is from the portal mysql_db


2.1 sumstats_in
~~~~~~~~~~~~~~~

  These need to be create per dataset/phenotype

        SNP  CHR     POS  A1  A2   REF   EAF                   Beta      se         P      N  INFO 
  -------------------------------------------------------------------------------------------------
   1:909221    1  909221  T   C,G  T    0.03      0.181299999999997  0.1029  0.078065  49324     1 
   1:913889    1  913889  G   A    G     0.6     0.0103999999999999   0.035   0.76611  49324     1 
   1:914333    1  914333  C   G    C    0.61   -0.00649999999999966   0.035   0.85142  49324     1 
   1:914852    1  914852  G   C    G     0.6  -0.000799999999999676  0.0351   0.98175  49324     1 
   1:914940    1  914940  T   C    T    0.59    0.00850000000000043  0.0347   0.80604  49324     1 
   1:916549    1  916549  A   G    A    0.76    0.00380000000000207  0.0405   0.92606  49324     1 
   1:916590    1  916590  G   A    G    0.16     0.0577999999999977   0.052   0.26621  49324     1 
   1:916834    1  916834  G   A    G     0.6    0.00439999999999576  0.0344   0.89923  49324     1 
   1:917640    1  917640  G   A    G     0.2     0.0283000000000045  0.0421   0.50133  49324     1 



  EAF is effective allele frequency from 1kg table


2.2 snp_list
~~~~~~~~~~~~

  corresponds to sumstats in

        SNP  A1  A2 
  ------------------
    1:88236  C   T  
    1:99719  C   T  
   1:171529  A   G  
   1:618463  G   A  
   1:693731  A   G  
   1:701946  A   G  
   1:704367  T   C  
   1:706645  A   C  
   1:708075  A   G  


2.3 munge_results
~~~~~~~~~~~~~~~~~

  output of munge_stats and input into ldscore regression

        SNP  A1  A2       Z           N 
    1:88236                             
    1:99719                             
   1:171529  A   G    0.498  100000.000 
   1:618463  G   A    0.181  100000.000 
   1:693731  A   G   -1.052  100000.000 
   1:701946  A   G   -0.924  100000.000 
   1:704367  T   C    0.629  100000.000 
   1:706645                             
   1:708075                             


3 LDscore regression
====================

3.1 Reformatting Description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Because the public datasets use rs Ids and the portal uses chrom pos
  all of the input files need to be formatted replacing rsId with
  chr:pos so that variants identifiers are compatible with data from
  portal mysql database.  For each component of the regression model
  there are 4 data files that need to be either reformatted with new ids
  or copied so that they remain as a set of file

  '*annot.gz (reformat)

  '*1.l2.M (copy)

  '*1.l2.M_5_50 (copy)

  '*ld_score.gz (reformat in 1000G_Phase3_baseline_ldscores.tgz, copy in
  Multi_tissue_gene_expr_1000Gv3_ldscores.tgz)


3.2 File types:
~~~~~~~~~~~~~~~

3.2.1 File 1.  .annot.gz* reformat
----------------------------------

  if reformating for 1000G_Phase3_baseline_ldscores.tgz otherwise copy

   CHR     BP  SNP           CM  base  Coding_UCSC.bed  Coding_UCSC.extend.500.bed  Conserved_LindbladToh.bed  etc           
     1  11008  rs575272151  0.0     1                0                           0                          0    0           
     1  11012  rs544419019  0.0     1                0                           0                          0    0           
     1  13110  rs540538026  0.0     1                0                           0                          0    0           

  converted to

   CHR     BP      SNP   CM  base  Coding_UCSC.bed  Coding_UCSC.extend.500.bed  Conserved_LindbladToh.bed  etc 
     1  11008  1:11008  0.0     1                0                           0                          0    0 
     1  11012  1:11012  0.0     1                0                           0                          0    0 
     1  13110  1:13110  0.0     1                0                           0                          0    0 


3.2.2 File 2. baseline.1.l2.M*
------------------------------

  copy file


3.2.3 File 3. baseline.1.l2.M_5_50*
-----------------------------------

  copy file


3.2.4 File 4. ldscore.gz*
-------------------------

  convert
   CHR  SNP             BP  All_Genes 
     8  rs11780869  164984    112.379 
     8  rs10097920  166851    100.675 
     8  rs2003497   176818     98.939 
     8  rs17744505  179693     46.317 
     8  rs17744517  182340     43.846 
     8  rs2906326   184319     97.953 
     8  rs10503143  184976     98.034 
     8  rs12676364  185300     21.253 
     8  rs2906328   187639     96.520 
  to
   CHR       SNP      BP  All_Genes 
     8  8:164984  164984    112.379 
     8  8:166851  166851    100.675 
     8  8:176818  176818     98.939 
     8  8:179693  179693     46.317 
     8  8:182340  182340     43.846 
     8  8:184319  184319     97.953 
     8  8:184976  184976     98.034 
     8  8:185300  185300     21.253 
     8  8:187639  187639     96.520 


3.3 Command
~~~~~~~~~~~

  python ldscore

  --h2-cts [ output from munge stats]

  --ref-ld-chr <baseline.> [ 1000G_Phase3_baseline_ldscores.tgz ]

  --out output

  --ref-ld-chr-cts GTEx.ldcts [
    Multi_tissue_gene_expr_1000Gv3_ldscores.tgz in S3 dig-ldscore]

  --w-ld-chr <weights.> [ weights_hm3_no_hla.tgz in S3 dig-ldscore]


3.4 Run
~~~~~~~

  Run munge stats then ldscore regression on dataset from each phenotype
  that has the most samples.


4 Load
======

  The output from LD score regression is .cell_type_results.txt For,
  example

   Name                                     Coefficient  Coefficient_std_error  Coefficient_P_value 
   Cervix_Endocervix                  5.94314247987e-08      2.67185268672e-08      0.0130623650369 
   Ovary                              5.59184672159e-08       2.5694901906e-08       0.014768377719 
   Pancreas                           5.27896455174e-08      2.75796265738e-08      0.0278048888108 
   Cells_EBV-transformed_lymphocytes   4.4279951454e-08        2.427585219e-08      0.0340735543031 
   Uterus                             4.99547354379e-08      2.97443340682e-08      0.0465301792091 
   Liver                              4.72685014049e-08      3.04224346555e-08      0.0601234286061 
   Kidney_Cortex                       4.4196990345e-08      2.90816953203e-08      0.0642865473491 
   Cervix_Ectocervix                  3.84330319794e-08      2.56225768373e-08       0.066811413437 
   Whole_Blood                        4.71459572675e-08      3.16928951163e-08      0.0684298449304 

  insert into ld_score(phenotype,tissue,weight,coef,se,p_value)"; |
  values(<PHENOTYPE>,<TISSUE_NAME>,<WEIGHT>,<COEF>,<SE>,<PVALUE>)

  PHENOTYPE=phenotype of dataset TISSUE=Tissue name
  WEIGHT=-log10(Coefficient_P_value) COEF=Coefficient
  SE=Coefficient_std_error PVALUE=Coefficient_P_value
