
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

run this step only on one r2 value so commands arent' repeated.
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
