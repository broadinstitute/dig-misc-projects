				________

				 README

				 tgreen
				________


Table of Contents
_________________

1 Overview of defining a SNP block
2 Getting resources
.. 2.1 Step (1) Run plink to get pairwise r2 values
.. 2.2 Step (2) Download hotspots and liftOver build from 34->37
..... 2.2.1 Record of liftOver done via web
3 Initial testing run
.. 3.1 Run plink to get pairwise R2
.. 3.2 combine r2 and hotspot file
4 LAP pipeline run


1 Overview of defining a SNP block
==================================

  DAPPLE method to define block around a variant is to 1) get variants
  farthest from primary variant with r2>0.5 in both directions then 2)
  exteneded that region to nearest recombination hotspot in both
  directions


2 Getting resources
===================

2.1 Step (1) Run plink to get pairwise r2 values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  plink --bfile --r --ld-window-r2 0.5


2.2 Step (2) Download hotspots and liftOver build from 34->37
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Details on download and liftOver
  [http://mathgen.stats.ox.ac.uk/oxstats_map/README.txt]

  wget [http://mathgen.stats.ox.ac.uk/oxstats_map/hotspots.txt]

  Recombination Rate map.  Not needed if hotspot file works(here for
  reference)
  [ftp://ftp.ncbi.nlm.nih.gov/hapmap/recombination/2011-01_phaseII_B37/genetic_map_HapMapII_GRCh37.tar.gz]


2.2.1 Record of liftOver done via web
-------------------------------------

* 2.2.1.1 From downloaded hotspot file make input files for UCSC liftOver of center , start and end of hotspot

  awk 'NR>1{print "chr"$1":"$2"-"$2+1}' hotspots.txt >
  Hotspot_Center.liftoverIn

  awk 'NR>1{print "chr"$1":"$3"-"$3+1}' hotspots.txt >
  Hotspot_Start.liftoverIn

  awk 'NR>1{print "chr"$1":"$4"-"$4+1}' hotspots.txt >
  Hotspot_End.liftoverIn


* 2.2.1.2 Run liftOver via web

  URL [https://genome.ucsc.edu/cgi-bin/hgLiftOver]


  + 2.2.1.2.1 Center of hotspot

    Set option Original assembly to hg16 and new assembly to hg19 Choose
    file Hotspot_Center.liftoverIn Submit file

    Successfully converted 26162 records: View Conversions Conversion
    failed on 15 records.  Display failure file Explain failure messages
    Failed input regions:

    Output: hglft_genome_4de4_a643d0.bed

    mv hglft_genome_4de4_a643d0.bed Hotspot_Center.bed open file
    Hotspot_Center.failure copy in failures


  + 2.2.1.2.2 Start of hotspot

    Set Original assembly to hg16 and new assembly to hg19 Choose file
    Hotspot_Start.liftoverIn Submit file

    Successfully converted 26171 records: View Conversions Conversion
    failed on 6 records.  Display failure file Explain failure messages

    Failed input regions:

    mv hglft_genome_4d5d_a67f80.bed Hotspot_Start.bed open file
    Hotspot_Start.failure copy in failures


  + 2.2.1.2.3 End of hotspot

    Set option Original assembly to hg16 and new assembly to hg19 Choose
    file Hotspot_End.liftoverIn Submit file Successfully converted 26172
    records: View Conversions

    Conversion failed on 5 records.  Display failure file Explain
    failure messages

    Failed input regions:

    mv hglft_genome_5483_a68dc0.bed Hotspot_End.bed open file
    Hotspot_End.failure copy in failures


* 2.2.1.3 combine liftovers

  perl combine_liftovers.pl


3 Initial testing run
=====================

  An initial run


3.1 Run plink to get pairwise R2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  plink --bed
  /humgen/diabetes/users/tgreen/ld_pruning/out/projects/ld_pruning.v18/phase3_1kg_common/shapeit2_mvncall_integrated_v4.20130502.chr19.bed
  \ --bim
  /humgen/diabetes/users/tgreen/ld_pruning/out/projects/ld_pruning.v18/phase3_1kg_common/shapeit2_mvncall_integrated_v4.20130502.chr19.portal.bim
  \ --fam
  /humgen/diabetes/users/tgreen/ld_pruning/out/projects/ld_pruning.v18/phase3_1kg_common/shapeit2_mvncall_integrated_v4.20130502.chr19.fam
  \ --extract
  /humgen/diabetes/users/tgreen/ld_pruning/out/projects/ld_pruning.v18/phase3_1kg_common/shapeit2_mvncall_integrated_v4.20130502.chr19.portal.extract
  \ --out chr19.portal \ --r --ld-window-r2 0.5


3.2 combine r2 and hotspot file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  perl define_block.pl --hotspot-file
  /humgen/diabetes2/users/tgreen/projects/gwas_proximity/hotspots/chr19.hotspots.b37.txt
  \ --ld-file
  /humgen/diabetes2/users/tgreen/projects/gwas_proximity/r2/chr19.portal.ld
  > chr19.blocks


4 LAP pipeline run
==================

  /humgen/diabetes/users/tgreen/projects/gwas_proximity

  perl ../../lap/trunk/bin/run.pl --meta
  meta/gwas_proximity.09142018.meta --only-cmd cmd1

  perl ../../lap/trunk/bin/run.pl --meta
  meta/gwas_proximity.09142018.meta --only-cmd make_block --bsub
