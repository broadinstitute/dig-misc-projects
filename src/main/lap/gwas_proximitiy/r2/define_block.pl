BEGIN{
    push @INC,'/broad/software/free/Linux/redhat_6_x86_64/pkgs/perl_5.10.1/lib/5.10.1/';
    push @INC,'/broad/software/free/Linux/redhat_6_x86_64/pkgs/perl_5.10.1/lib/site_perl/5.10.1/';
    push @INC,'/home/unix/tgreen/perl5/lib/site_perl/5.10.1/';
    push @INC,'/home/unix/tgreen/dig-jenkins/lib/';
}

use strict;
use Getopt::Long;
use Pod::Usage;
use Config::Simple;
use Log::Log4perl;
use KeyArgs;

my $help;
my $man;
my $debug;
my $trace;
my $log_file_name='define_block.log';
my @param = @ARGV;
my $hotspot_file;
my $ld_file;
GetOptions(
    'trace'                         => \$trace,
    'debug'                         => \$debug,
    'help'                          => \$help,
    'man'                           => \$man,
    'hotspot-file=s'                => \$hotspot_file,
    'ld-file=s'                     => \$ld_file
    ) or pod2usage(-verbose         => 1) && exit;

pod2usage({-noperldoc => 1, -verbose => 1,-exitval=>1}) if defined $help;
pod2usage({-noperldoc => 1, -verbose => 2,-exitval=>1}) if defined $man;
pod2usage({-message=>"\n\n ERROR: --hotspot-file configured\n\n",-noperldoc => 1, -verbose => 2}) if (! -e $hotspot_file );
pod2usage({-message=>"\n\n ERROR: --ld-file configured\n\n",-noperldoc => 1, -verbose => 2}) if (! -e $ld_file );

my $log4perlconf = qq(
    log4perl.category.Foo.Bar        = INFO, Screen , Log
    log4perl.category.debugger       = DEBUG, Screen
    log4perl.category.tracer         = TRACE, Screen
    log4perl.appender.Screen         = Log::Log4perl::Appender::Screen
    log4perl.appender.Screen.stderr  = 1
    log4perl.appender.Screen.layout= PatternLayout
    log4perl.appender.Screen.layout.ConversionPattern=  %d %p %m%n
    log4perl.appender.Log            = Log::Log4perl::Appender::File
    log4perl.appender.Log.filename   = $log_file_name
    log4perl.appender.Log.mode       = append
    log4perl.appender.Log.layout= PatternLayout
    log4perl.appender.Log.layout.ConversionPattern=  %d %p %m%n
  );

Log::Log4perl::init( \$log4perlconf );
my $logger;
if($debug){
     $logger = Log::Log4perl->get_logger('debugger');
}elsif($trace){
     $logger = Log::Log4perl->get_logger('tracer');
}else{
     $logger = Log::Log4perl->get_logger('Foo.Bar');
}

$logger->info("Starting $0 @param");




open (HS,$hotspot_file)||die;
my @hotspots = <HS>;
my @reverse_hotspots=reverse(@hotspots);
chomp(@reverse_hotspots);
chomp(@hotspots);
close(HS);

open(F,$ld_file);

my %position;
my %chr;
my %variant_id;
my @variant;
my %r2;
<F>;
my %pair;
my %left;
my %right;
while(my $readline=<F>){
    my @this = split(/\s+/,$readline);
    my $locus1 = "$this[1]:$this[2]";
    my $locus2 = "$this[4]:$this[5]";
    if (!$position{$locus1}){
	#	push @variant,$this[3];
	push @variant,$locus1;
    }
    $variant_id{$locus1}=$this[3];
    $chr{$locus1}=$this[1];
    $position{$locus1}=$this[2];
    $left{$locus1}{$locus2}=$this[5];
    $right{$locus2}{$locus1}=$this[2];
    1;
}

foreach my $variant (@variant){
    if($variant eq '.'){
	1;
    }
    my $low_bound = get_low_boundary($variant);
    my $high_bound = get_high_boundary($variant);
    my $low_hs = find_low_hotspot($low_bound);
    my $high_hs = find_high_hotspot($high_bound);
    print "$variant_id{$variant} $chr{$variant}:$position{$variant} $low_hs $low_bound $high_bound $high_hs\n";
}

sub find_high_hotspot{
    my ($high_bound)=@_;
    for(my $h_idx=0;$h_idx<=$#hotspots;$h_idx++){
	my (undef,undef,$this_hs)=split(/\s+/,$hotspots[$h_idx]);
	if($this_hs>$high_bound){
	    return $this_hs;
	}
    }
    return $high_bound;
}


sub find_low_hotspot{
    my ($low_bound)=@_;
    for(my $rh_idx=0;$rh_idx<=$#reverse_hotspots;$rh_idx++){
	my (undef,undef,$this_hs)=split(/\s+/,$reverse_hotspots[$rh_idx]);
	if($low_bound>$this_hs){
	    return $this_hs;
	}
    }
    return $low_bound;
}



sub get_low_boundary{
    my ($variant) = @_;
    my $low_bound=$position{$variant};;
    for my $pair (keys %{$left{$variant}}){
	if ($left{$variant}{$pair} && ($left{$variant}{$pair} < $low_bound)){
	    $low_bound=$left{$variant}{$pair};
	}
    }
    for my $pair (keys %{$right{$variant}}){
	if ($right{$variant}{$pair} && ($right{$variant}{$pair} < $low_bound)){
	    $low_bound=$right{$variant}{$pair};
	}
    }

    
    return $low_bound;
}

sub get_high_boundary{
    my ($variant) = @_;
    my $high_bound=$position{$variant};;
    for my $pair (keys %{$left{$variant}}){
	if ($left{$variant}{$pair} && ($left{$variant}{$pair} > $high_bound)){
	    $high_bound=$left{$variant}{$pair};
	}
    }
    for my $pair (keys %{$right{$variant}}){
    	if ($right{$variant}{$pair} && ($right{$variant}{$pair} > $high_bound)){
	    $high_bound=$right{$variant}{$pair};
	}
    }

    return $high_bound;
}





=head1 NAME

 define_block.pl

=head1 SYNOPSIS







=head1 DESCRIPTION

 

=head1 OPTIONS

 debug                       set logger to DEBUG
 trace                       set logger to TRACE
 help                        help
 man                         manual



=head1 EXAMPLE

 perl define_block.pl --hotspot-file /humgen/diabetes2/users/tgreen/projects/gwas_proximity/hotspots/chr19.hotspots.b37.txt --ld-file /humgen/diabetes2/users/tgreen/projects/gwas_proximity/r2/chr19.portal.ld

 
=cut
