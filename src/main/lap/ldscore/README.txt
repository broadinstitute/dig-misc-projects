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
  There are several parts of this pipeline each with multiple steps.

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

  '*ld_score.gz (reformat)


3.2 File types:
~~~~~~~~~~~~~~~

3.2.1 File 1.  .annot.gz* reformat
----------------------------------

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
