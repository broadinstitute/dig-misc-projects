my %failed_center;
open(CENTER_FAILURE,"Hotspot_Center.failure")||die;
while(my $readline = <CENTER_FAILURE>){
    next if($readline=~/^#/);
    chomp $readline;
    $failed_center{$readline}=1;
}
my %center_build_37;
open(CENTER_IN,"Hotspot_Center.liftoverIn")||die;
open(CENTER_OUT,"Hotspot_Center.bed")||die;
while(my $input=<CENTER_IN>){
    chomp $input;
    if($failed_center{$input}){
	1;
    }else{
	$output=<CENTER_OUT>;
	chomp $output;
	$center_build_37{$input}=$output;
    }
}
1;


my %failed_start;
open(START_FAILURE,"Hotspot_Start.failure")||die;
while(my $readline = <START_FAILURE>){
    next if($readline=~/^#/);
    chomp $readline;
    $failed_start{$readline}=1;
}
my %start_build_37;
open(START_IN,"Hotspot_Start.liftoverIn")||die;
open(START_OUT,"Hotspot_Start.bed")||die;
while(my $input=<START_IN>){
    chomp $input;
    if($failed_start{$input}){
	1;
    }else{
	$output=<START_OUT>;
	chomp $output;
	$start_build_37{$input}=$output;
    }
}


my %failed_end;
open(END_FAILURE,"Hotspot_End.failure")||die;
while(my $readline = <END_FAILURE>){
    next if($readline=~/^#/);
    chomp $readline;
    $failed_end{$readline}=1;
}
my %end_build_37;
open(END_IN,"Hotspot_End.liftoverIn")||die;
open(END_OUT,"Hotspot_End.bed")||die;
while(my $input=<END_IN>){
    chomp $input;
    if($failed_end{$input}){
	1;
    }else{
	$output=<END_OUT>;
	chomp $output;
	$end_build_37{$input}=$output;
    }
}

1;
`rm chr*.hotspots.b37.txt`;
open(ALL,"paste Hotspot_Center.liftoverIn Hotspot_Start.liftoverIn Hotspot_End.liftoverIn|");
while(my $readline=<ALL>){
    chomp $readline;
    my ($center,$start,$end) = split(/\s+/,$readline);
    
    if($center_build_37{$center} && $start_build_37{$start} && $end_build_37{$end}){
	$start_build_37{$start} =~m/chr(.+):(\d+)-(\d+)/;

	$start_chr = $1;
	$start_pos = $2;
	open(OUT,">>chr${start_chr}.hotspots.b37.txt")||die;
	$end_build_37{$end} =~m/chr(.+):(\d+)-(\d+)/;
	$end_chr = $1;
	$end_pos = $2;
	print OUT "$start_chr $start_pos $end_pos\n";
	close(OUT);
    }else{
	1;
    }
}


#Hotspot_Center.liftoverIn
#Hotspot_Center.bed
#Hotspot_Center.failure
