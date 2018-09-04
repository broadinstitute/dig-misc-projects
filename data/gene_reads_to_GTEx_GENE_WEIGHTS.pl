#!/usr/bin/perl -w

#HOW TO NORMALIZE THE DATA
#1 -> log10($_+1)/$log10maxMedianPlusOne;
#2 -> by median across the tissues
#3 -> by mean across the tissues
#4 -> to Z-score
#any other -> do not normalize

$NORMALIZE = 4;

#open file with GTEx IDs and take only TruSeq
open(IN,"cut -f1,7,16 GTEx_v7_Annotations_SampleAttributesDS.txt |") || die;
$header = <IN>;
while(<IN>) {
	chomp;
	($id,$tissue,$tech) = split /\t/, $_;
	next if $tech ne "TruSeq.v1";
	$tissue =~ s/[( \-]+/_/g;
	$tissue =~ s/\)$//g;
	$id2tissue{$id} = $tissue;
}

#open file with reads count
open(IN,"gzip -cd GTEx_Analysis_2016-01-15_v7_RNASeQCv1.1.8_gene_reads.gct.gz |") || die;

#read and analyze header
for($i=0;$i<3;$i++) { chomp($header=<IN>) }
@header=split /\t/,$header;
for($i = 2; $i < @header; $i++) {
	die if !exists $id2tissue{$header[$i]};
	$tissue = $id2tissue{$header[$i]};

	if(!exists $tissue2startIndex{$tissue}) {
		$tissue2startIndex{$tissue} = $i;
	}
	else {
		$tissue2endIndex{$tissue} = $i;
	}	
}

$lastIndex = 1; #check if everything is ok, i.e. indexes are sorted in the input file
foreach $tissue (sort {$tissue2startIndex{$a} <=> $tissue2startIndex{$b}} keys %tissue2startIndex) {
	push @sortedTissues, $tissue;
	die $tissue if $tissue2startIndex{$tissue} - $lastIndex != 1;
	$lastIndex = $tissue2endIndex{$tissue};
}

#read the info about all reads
$maxMedian = 0;
while(<IN>) {
	chomp;
	@data = split /\t/, $_;
	push @geneIDs,   $data[0];
	push @geneNames, $data[1];
	foreach $tissue (@sortedTissues) {
		@reads = ();
		for($i = $tissue2startIndex{$tissue}; $i <= $tissue2endIndex{$tissue}; $i++) {
			push @reads, $data[$i];
		}
		@reads = sort { $a <=> $b } @reads;
		$median = @reads%2 ? $reads[int(@reads/2)] : ($reads[int(@reads/2)-1] + $reads[int(@reads/2)])/2;
		push @weights, $median;
		$maxMedian = $median if $maxMedian < $median;
	}
}

if($NORMALIZE == 1) {
	#normalize weights to have a range from 0 to 1
	$log10maxMedianPlusOne = log($maxMedian+1)/log(10);
	foreach(@weights) {
		$_ = log($_+1)/log(10)/$log10maxMedianPlusOne;
	}
}
elsif($NORMALIZE == 2) {
	#normalize by deviding by tissue median
	@data = ();
	$medianN = int(@sortedTissues/2);
	for($i = 0; $i < @geneIDs; $i++) {
		for($j = 0; $j < @sortedTissues; $j++) {
			$data[$j] = $weights[$i * @sortedTissues + $j];
		}
		@data = sort { $a <=> $b } @data;
		for($n = $medianN; $n < @sortedTissues; $n++) {
			last if $data[$n] > 0;
		}
		next if $n == @sortedTissues;
		$median = $data[$n];
		for($j = 0; $j < @sortedTissues; $j++) {
			$weights[$i * @sortedTissues + $j] /= $median;
		}
	}
}
elsif($NORMALIZE == 3) {
	#normalize by deviding by mean across tissues
	for($i = 0; $i < @geneIDs; $i++) {
		$mean = 0;
		for($j = 0; $j < @sortedTissues; $j++) {
			$mean += $weights[$i * @sortedTissues + $j];
		}
		$mean /= @sortedTissues;
		next if $mean == 0;
		for($j = 0; $j < @sortedTissues; $j++) {
			$weights[$i * @sortedTissues + $j] /= $mean;
		}
	}
}
elsif($NORMALIZE == 4) {
	#normalize to z-score by tissue
	for($i = 0; $i < @geneIDs; $i++) {
		$mean = 0;
		for($j = 0; $j < @sortedTissues; $j++) {
			$mean += $weights[$i * @sortedTissues + $j];
		}
		$mean /= @sortedTissues;
		$stdv = 0;
		for($j = 0; $j < @sortedTissues; $j++) {
			$stdv += ($weights[$i * @sortedTissues + $j] - $mean)**2;
		}
		$stdv = sqrt($stdv/(@sortedTissues-1));
		next if $stdv == 0;
		for($j = 0; $j < @sortedTissues; $j++) {
			$weights[$i * @sortedTissues + $j] -= $mean;
			$weights[$i * @sortedTissues + $j] /= $stdv;
		}
	}
}


#print output table
print "GEN_ID\tGENE";
foreach(@sortedTissues) { print "\t$_" }
print "\n";
for($i = 0; $i < @geneIDs; $i++) {
	print "$geneIDs[$i]\t$geneNames[$i]";
	for($j = 0; $j < @sortedTissues; $j++) {
		print "\t", $weights[$i * @sortedTissues + $j];
	}
	print "\n";
}
