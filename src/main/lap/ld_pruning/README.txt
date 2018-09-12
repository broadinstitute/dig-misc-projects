
This pipeline requires manual steps as it exists now.  This is a description of the steps and how to run.  
There are notes on how to run the pipeline using the UGER cluster.  There are also some notes on how one could
run this pipeline outside of UGER, though this would not be the ideal method.

LAP PIPELINE COMMANDS
1. make_genomewide_input - plink command to extract common variants from phase3 1kg into a vcf file
2. ld_get_variant_ids - this creates plink .bim files and .extract list for plink files generated in 1 using portal variant ids
3. cmd_make_dataset_meta_file - creates a meta data file to create objects of class dataset for clumping and database upload
4. ld_get_plink_annot_from_portal - for each dataset extract variants passing a pvalue significance threshold and write summary stats used in clump.
5. ld_run_clump - runs clump on each chromosome,dataset and r2
6. make_clump_exclude - parses output from step 5. to get all variants to exclude at a r2 value
7. sql_loader*        - these commands create exclude .sql files for data updload at each r2 value.  eg. pointone finds all exclude uniqu to pointone only.
                                                                                                         pointtwo find unique to pointtwo or pointone
                                                                                                         etc.
   sql_loader_pointone
   sql_loader_pointtwo
   sql_loader_pointfour
   sql_loader_pointsix
   sql_loader_pointeight
8. sql_upload_cmd - upload .sql files to database


How to Run
meta/ld_pruning_v18.meta is for common dv18

Note:  some steps are run on only one r2 file so commands arent' repeated.
1. perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_genomewide_input --only pointone
2. perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd ld_get_variant_ids --only pointone (modify cluster usage parameters for MySQL*
3. perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd cmd_make_dataset_meta_file
4. perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd ld_get_plink_annot_from_portal --only pointone
5. perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd run_clump --bsub
6. perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_clump_exclude --bsub
7. perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_loader_point --bsub ( this will run all sql_loader_point*)
8. perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_upload_cmd --bsub *
/* to limit the number of jobs running on db uncomment these lines.  This should be taken care of by bsub_batch option but I have not been 
able to get this working so I using these configuration options on database access jobs.
  key max_jobs 2 
  key max_sge_batch 10


## due to the cluster being backlogged, this method enables parallizing the processes.  It uses a Unix pipeline to extract dataset objects from meta file and runs each dataset and r2 separately
# To enable run clump to run on vm
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd run_clump --only pointone  --only {} --force-started
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd run_clump --only pointtwo  --only {} --force-started
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd run_clump --only pointfour  --only {} --force-started
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd run_clump --only pointsix  --only {} --force-started
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd run_clump --only pointeight  --only {} --force-started
# To enable make exclude to run on vm
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_clump_exclude --only pointone --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_clump_exclude --only pointtwo --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_clump_exclude --only pointfour --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_clump_exclude --only pointsix --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_clump_exclude --only pointeight --only {}
# To enable sql file generation to run on vm
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_loader_pointone --only pointone --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_loader_pointtwo --only pointtwo --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_loader_pointfour --only pointfour --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_loader_pointsix --only pointsix --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_loader_pointeight --only pointeight --only {}
# To enable sql upload to run on vm
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_upload_cmd --only pointone --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_upload_cmd --only pointtwo --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_upload_cmd --only pointfour --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_upload_cmd --only pointsix --only {}
grep class ../../ld_pruning/out/projects/ld_pruning.v18/ld_pruning.v18.dataset.meta  | awk '{print $1}' | xargs -i perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_upload_cmd --only pointeight --only {}


Misc testing calls
----
perl lap/trunk/bin/run.pl --meta projects/ld_pruning/ld_pruning.meta --debug --bsub
# create vcf files for 1kg common variants
# run only on one r2
perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_genomewide_input --check --only pointone
# takes a bim file and returns a bim file with portal ids and a snp extract list of variants in portal
# run only on one r2
# test on chrom22
perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd ld_get_variant_ids --check --only pointone --only 22

# makes annot file required for clumping
# run only on one r2
# test on chrom 22 & ExChip_300k_dv1__CHOL
perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd ld_get_plink_annot_from_portal --only pointone --only 22 --only ExChip_300k_dv1__CHOL 


#run clump
perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd run_clump --only pointtwo --only 22 --only ExChip_300k_dv1__CHOL 

#make exclude
perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd make_clump_exclude  --only 22 --only ExChip_300k_dv1__CHOL

perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_loader_point* --only 22 --only ExChip_300k_dv1__CHOL

perl ../../lap/trunk/bin/run.pl --meta meta/ld_pruning_v18.meta --only-cmd sql_upload_cmd --only 22 --only ExChip_300k_dv1__CHOL
