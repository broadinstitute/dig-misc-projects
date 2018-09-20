				________

				 README

				 tgreen
				________


Table of Contents
_________________

1 Clumping
2 Steps
.. 2.1 Extract common variants (minor allele frequence > 5%) from 1000 Genomes
.. 2.2 Create  plink .bim and .extract files for all common variants using portal-based IDs
.. 2.3 Create .annot file containing association statistice for the dataset being clumped
.. 2.4 Run Clump
.. 2.5 Make Exclude
.. 2.6 Make Unique Exclude SQL
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
  1) reference genotype dataset (1000 Genomes) for linkage
     disequilibrium(LD) statistics
  2) association statistics for the dataset being clumped.


  Reference for description of parameters and how clumping works
  [http://zzz.bwh.harvard.edu/plink/clump.shtml]


2 Steps
=======

  There are a few pre-processing steps to get the data in the correct
  format for clumping.  Once the data is corrected formatted the command
  plink --clump (with options) is used to clump the data.  After the
  data has been clumped there are a few steps to parse and reformat the
  data for upload.


2.1 Extract common variants (minor allele frequence > 5%) from 1000 Genomes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  PLINK binary filessets consist of 3 files .bed,.bim,and .fam.  .bed
  files have the genotypes,.bim files have the markers and .fam files
  have the sample information.

  To create plink .bed,.bim,.fam files for common variants of 1000
  Genomes the command is

  plink --vcf-half-call missing

  --maf 0.05

  --make-bed

  --vcf <1000Genomes>

  --out <chrm>



  Rare variants will not be included in exclude files.


2.2 Create  plink .bim and .extract files for all common variants using portal-based IDs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  From the .bim file for common variants run a series of SQL commands to
  get corresponding variant IDs in portal format.  The portal .bim file
  will then be compatible with the .annot file of association statistics
  for the clumping computation.

  get_variant_ids.pl reads in .bim file from common variants plink
  binary fileset created above and creates 2 new files

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

  For clumping, plink needs the association statistics for each dataset
  and chromosome for each dataset


  script get_plink_annot_from_portal.pl

  produces


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

  plink --clump-p1 0.1

  -clump-p2 0.1

  -clump-r2 [.1,.2,.4,.6,.8]

  --allow-no-sex

  --noweb

  --bed phase3_1kg_common_bed

  --bim portal_bim

  --fam phase3_1kg_common_fam

  --clump portal_association_annot

  --extract,portal_snp_extract

  --chr p<chr>

  --out


   CHR  F  SNP                    BP         P  TOTAL  NSIG  S05  S01  S001  S0001  SP2                                       
  ----------------------------------------------------------------------------------------------------------------------------
    17  1  17_79415386_C_T  79415386  1.57e-05     17     6    9    2     0      0  17_79412885_T_A(1),17_79413112_C_A(1),etc 
    17  1  17_79036337_C_G  79036337  2.66e-05      3     0    0    3     0      0  17_79033694_C_T(1),17_79034115_A_G(1),etc 
    17  1  17_77935805_C_T  77935805  2.86e-05     13     0    2    4     2      5  17_77928017_C_G(1),17_77929817_T_G(1),etc 


  Variants in SP2 are represented by variant in SNP


2.5 Make Exclude
~~~~~~~~~~~~~~~~

  This step takes the last column of the previous step and creates list
  of variants that can be excluede at each r2 level perl -lane 'my
  \$this= \$F[1];

  my @a=split(",",\$this);

  map {s/\(.+\)//g;} @a;

  foreach \$a (@a)

  {print \$a if length(\$a)>5}' clump_file > clump_exclude


   17_79413436_T_C 
   17_79413475_C_A 
   17_79414307_A_G 
   17_79414914_A_G 
   17_79415766_G_A 
   17_79416454_A_G 
   17_79417528_T_C 
   17_79418260_A_G 


2.6 Make Unique Exclude SQL
~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Next step is to make succesive unique exclude lists into sql format
  for upload.  Find all excludes unique to .1,then to .2 then .4 etc.
  Basic idea cat list.1 list.2 list.2 list.4 list.4 list.6 list.6 list.8
  list.8 | sort | uniq > uniq.q


   17_10023426_C_T  WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_102384_T_A    WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_10393249_G_T  WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_10522041_G_T  WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_10524747_A_G  WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_10711174_C_A  WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_10902666_T_C  WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_10924652_C_T  WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_10947_C_T     WGS_GoT2D_dv1__T2D  T2D  0.1 
   17_10967062_G_C  WGS_GoT2D_dv1__T2D  T2D  0.1 


2.7 Upload SQL
~~~~~~~~~~~~~~

  Final step is to upload files from previous step to db



Footnotes
_________

[1] DEFINITION NOT FOUND.
