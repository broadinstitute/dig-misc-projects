				________

				 README

				 tgreen
				________


Table of Contents
_________________

1 Clumping
2 Steps
.. 2.1 Extract common variants (minor allele frequence > 5%) from 1000 Genomes
.. 2.2 Create plink .bim and .extract files for all common variants
.. 2.3 Create .annot file containing association statistice for the dataset being clumped
.. 2.4 Run Clump
.. 2.5 Make Exclude
.. 2.6 Make Unique Exclude SQl
.. 2.7 Upload SQL


1 Clumping
==========

  'Clumping' is grouping a set of variants because they are correlated
  in genotype space and representing that clump of variants by the
  variant with the lowest pvalue of association to a phenotype.  The
  purpose of this pipeline is to create a list of variants that can be
  excluded from viewing because they are represented by another variant
  that has a lower association p-value to phenotype and have an r2 >
  somethreshold.

  The clumping algorithm requires a
  1) reference genotype dataset (1000 Genomes) and
  2) association statistics for the dataset being clumped.


  Reference for description of parameters and how clumping works
  [http://zzz.bwh.harvard.edu/plink/clump.shtml]


2 Steps
=======

  There are a few preprocessing steps to get the data in the correct
  format for clumping.  The command plink --clump is used to clump the
  data.  Once the data have there are a few steps to reformat the data
  for upload into dataset.


2.1 Extract common variants (minor allele frequence > 5%) from 1000 Genomes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  To create plink bed files for common variants of 1000 Genomes.  Rare
  variants will not be included in exclude files.  plink_cmd
  --vcf-half-call missing --maf 0.05 --make-bed --vcf <1000Genomes>
  --out <chrm>


2.2 Create plink .bim and .extract files for all common variants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  From the .bim file for common variants run sql command to get variant
  IDs in portal format.  The bim file will then be compatible with the
  .annot file of association statistics for the clumping computation.

  get_variant_ids.pl reads in .bim file from common variants created
  above and creates 2 files

  Output file 1 .bim file with portal IDs (chr_pos_ref_alt).  If there
  is not a variant in portal the rs number is is used.

   9  rs141734683    0  10362  C  CT 
   9  9_10469_G_C    0  10469  G  C  
   9  9_14690_C_G    0  14690  C  G  
   9  rs71509923     0  14863  G  A  
   9  9_14889_A_G    0  14889  G  A  
   9  9_15883_A_G    0  15883  G  A  
   9  .              0  16934  A  G  
   9  rs202245356    0  16967  G  A  
   9  rs78210423     0  17107  C  T  
   9  9_17115_G_C,T  0  17115  C  G  


  Output file 2 .extract file containing only variants that are in the
  portal.  This file is used to limit the variants used in clumping to
  those in the portal.

   9_10469_G_C   
   9_14690_C_G   
   9_14889_A_G   
   9_15883_A_G   
   9_17115_G_C,T 
   9_39037_A_C   
   9_39516_C_T   
   9_40178_A_G   
   9_40910_T_G   
   9_40997_A_T   


2.3 Create .annot file containing association statistice for the dataset being clumped
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  get_plink_annot_from_portal.pl

   CHROM  SNP                 BP  A1    F_A  F_U  A2  CHISQ          P                  BETA 
  -------------------------------------------------------------------------------------------
       1  1_30967_CCCA_C   30966  CCCA    0    0  -       0   0.089331   -0.5557899999999999 
       1  1_66596_AT_A     66595  AT      0    0  -       0    0.02244    0.5943000000000004 
       1  1_147591_G_GA   147591  G       0    0  A       0  0.0072203              -0.87507 
       1  1_413994_CA_C   413993  CA      0    0  -       0   0.097916   -0.5185199999999998 
       1  1_653062_TA_T   653061  TA      0    0  -       0   0.088741    0.3804700000000016 
       1  1_682462_AG_A   682461  AG      0    0  -       0   0.043422    0.4764399999999992 
       1  1_693731_A_G    693731  A       0    0  G       0  0.0071156  -0.22431000000000054 
       1  1_729632_C_T    729632  C       0    0  T       0   0.085771              -0.77467 
       1  1_729679_C_G    729679  C       0    0  G       0   0.038137    0.1532400000000013 


2.4 Run Clump
~~~~~~~~~~~~~

  Here is the clump command short cmd ld_run_clump=plink\ --clump-p1 0.1
  \ -clump-p2 0.1 \ -clump-r2 [.1,.2,.4,.6,.8] \ --allow-no-sex \
  --noweb \ --bed,phase3_1kg_common_bed --bim,portal_bim
  --fam,phase3_1kg_common_fam --clump portal_association_annot
  --extract,portal_snp_extract --chr <chr> --out


2.5 Make Exclude
~~~~~~~~~~~~~~~~


2.6 Make Unique Exclude SQl
~~~~~~~~~~~~~~~~~~~~~~~~~~~


2.7 Upload SQL
~~~~~~~~~~~~~~
