				________

				 README

				 tgreen
				________


Table of Contents
_________________

1 Description
2 Munge stats
3 LDscore regression
.. 3.1 Command
.. 3.2 Reformatting Description
.. 3.3 File types:
..... 3.3.1 File 1.  .annot.gz* reformat
..... 3.3.2 File 2. baseline.1.l2.M*
..... 3.3.3 File 3. baseline.1.l2.M_5_50*
..... 3.3.4 File 4.  ldscore.gz*
.. 3.4 Model Components
..... 3.4.1 baseline.
..... 3.4.2 cell type specific
.. 3.5 Run
4 Load


1 Description
=============

  Pipeline to get cell-type specific LD score regression statistics.
  There are several parts of this pipeline each with multiple steps.

  Software can be downloaded from

  [https://github.com/bulik/ldsc]

  Information about data to download can be found at

  [https://github.com/bulik/ldsc/wiki/Cell-type-specific-analyses]


2 Munge stats
=============

  python /humgen/diabetes/users/tgreen/software/ldsc/munge_sumstats.py
  --sumstats <sumstats_in> --merge-alleles <snp_list> --out
  <munge_result>

  The data input for these steps is from the portal mysql_db sumstats_in

        SNP  CHR     POS  A1  A2  REF     EAF                 Beta      se       P       N  INFO 
  -----------------------------------------------------------------------------------------------
    1:88236    1   88236  C   T   C    0.0026  -0.0237805286654034  0.1171  0.8393  100000     1 
    1:99719    1   99719  C   T   C    0.0013   -0.061343630241052  0.1203  0.6102  100000     1 
   1:171529    1  171529  A   G   A      0.02   0.0557241487723602   0.112  0.6187  100000     1 
   1:618463    1  618463  G   A   G      0.09  0.00995033085316809  0.0549  0.8565  100000     1 
   1:693731    1  693731  A   G   A      0.12  -0.0750147038054455  0.0713   0.293  100000     1 
   1:701946    1  701946  A   G   A      0.94  -0.0486949215387585  0.0527  0.3553  100000     1 
   1:704367    1  704367  T   C   T      0.95   0.0379095730732221  0.0603  0.5292  100000     1 
   1:706645    1  706645  A   C   A    0.0026   0.0178585183013094  0.0649  0.7834  100000     1 
   1:708075    1  708075  A   G   A    0.0026    0.041551427158234  0.0666  0.5325  100000     1 

  EAF is effective allele frequency from 1kg table

  snp_list
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


  output munge_results
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

3.1 Command
~~~~~~~~~~~

  python ldscore

  --h2-cts sumstats

  --ref-ld-chr <baseline.>

  --out <munge_result>

  --ref-ld-chr-cts GTEx.ldcts

  --w-ld-chr <weights.>


3.2 Reformatting Description
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

  '*ld_score.gz (reformat)


3.3 File types:
~~~~~~~~~~~~~~~

3.3.1 File 1.  .annot.gz* reformat
----------------------------------

   CHR     BP  SNP           CM  base  Coding_UCSC.bed  Coding_UCSC.extend.500.bed  Conserved_LindbladToh.bed  etc           
     1  11008  rs575272151  0.0     1                0                           0                          0    0           
     1  11012  rs544419019  0.0     1                0                           0                          0    0           
     1  13110  rs540538026  0.0     1                0                           0                          0    0           

  converted to

   CHR       BP  SNP           CM  base  Coding_UCSC.bed  Coding_UCSC.extend.500.bed  Conserved_LindbladToh.bed  etc 
     1  1:11008  rs575272151  0.0     1                0                           0                          0    0 
     1  1:11012  rs544419019  0.0     1                0                           0                          0    0 
     1  1:13110  rs540538026  0.0     1                0                           0                          0    0 


3.3.2 File 2. baseline.1.l2.M*
------------------------------

  copy file


3.3.3 File 3. baseline.1.l2.M_5_50*
-----------------------------------

  copy file


3.3.4 File 4.  ldscore.gz*
--------------------------

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


3.4 Model Components
~~~~~~~~~~~~~~~~~~~~

  Each of the model compenents will have the 4 file types by chromosome
  and tissue


3.4.1 baseline.
---------------

  --ref-ld-chr Data downloaded from web
  ----------------------------------------------------------------------
  /humgen/diabetes/users/tgreen/ldscore/out/projects/experiment1/1000G_EUR_Phase3_baseline/


3.4.2 cell type specific
------------------------

    --ref-ld-chr-cts
  /humgen/diabetes/users/tgreen/ldscore/out/projects/project1/GTEx.ldcts
  ( which points to data here This file points to groups of files per
  tissue.  For example GTEx.1. and GTEx.control. from line 1 will have 8
  (4+4)files to reformat or copy.  The example lists 10 tissues.  There
  are 53 tissues in the GTex dataset.

   Adipose_Subcutaneous                    GTEx.1.,GTEx.control.  
   Adipose_Visceral_(Omentum)              GTEx.2.,GTEx.control.  
   Adrenal_Gland                           GTEx.3.,GTEx.control.  
   Artery_Aorta                            GTEx.4.,GTEx.control.  
   Artery_Coronary                         GTEx.5.,GTEx.control.  
   Artery_Tibial                           GTEx.6.,GTEx.control.  
   Bladder                                 GTEx.7.,GTEx.control.  
   Brain_Amygdala                          GTEx.8.,GTEx.control.  
   Brain_Anterior_cingulate_cortex_(BA24)  GTEx.9.,GTEx.control.  
   Brain_Caudate_(basal_ganglia)           GTEx.10.,GTEx.control. 

  In each of this groups all the file types need to be converted or
  copied.


3.5 Run
~~~~~~~


4 Load
======
