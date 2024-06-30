#!/usr/bin/perl
use strict;
use warnings;
use File::Basename;
use Data::Dumper;

# drops field PHOTO

my $fileIn = 'd:\Archiv\Kontakte\2021\ab-torben-nc-2021-08-09.vcf';
my ( $fname, $fdir, $fext ) = fileparse( $fileIn, qr/\.[^.]*/ );
my $fileOut = "$fname-noPhotos$fext";

open( my $fhin, "<", $fileIn ) or die $!;
my $contOrig = join "", <$fhin>;
close $fhin;

my $cont = $contOrig;
$cont =~ s/\r\n/\n/g;    # Windows Linebreak -> Linux Linebreak

# Fields to remove
my @L = qw (
    PHOTO
);

# ADR
# ORG
# TITLE
# N
# TEL

# UID
# REV
# PRODID
# CATEGORIES
# NOTE
# ADR
# PRODID
# CLASS
# BDAY
# NICKNAME
# LABEL
# URL

# IMPP
# DAVDROID1
# X-MS-IMADDRESS
# X-DAVDROID-STARRED
# X-KPILOT-RECORDID
# X-KADDRESSBOOK-X-IMADDRESS
# X-KADDRESSBOOK-BLOGFEED
# X-ICQ

foreach my $cat (@L) {
  $cont =~ s/(?<=\n)$cat[;:].*?\n(?=\w)//sg
      ; # alles bis zum ersten Zeilenumbuch ohne Leerzeichen, sondern mit Wortzeichen dahinter
}

# $cont =~ s/;PREF=1//g;
# $cont =~ s/VERSION:4\.0/VERSION:3.0/g;

my %h;
while ( $cont =~ m/(?<=\n)(\w[^:]+)[:]/gc ) {
  $h{$1}++;
}

# by values, reverse
foreach my $k ( sort { $h{$b} <=> $h{$a} } keys(%h) ) {
  print "$h{$k}\t$k\n";

  #last if $h{$k}==1;
}

open( my $fhout, ">", $fileOut ) or die $!;
print $fhout $cont;
close $fhout;
