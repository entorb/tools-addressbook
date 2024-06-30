#!/usr/bin/perl
use strict;
use warnings;
use 5.010;

# by Torben Menke http:/entorb.net

# Auswertung der Keys aller VCards eines Adressbuchs

# pp -u -o script.exe script.pl & copy script.exe c:\tmp

# TODO

# IDEAS

# DONE

# Perl Standard Modules
use Data::Dumper;
use File::Basename;
use utf8;
use open ":encoding(UFT-8)";    # for all files
use Encode;
my $encodingSay = 'CP850';      # Linux: 'UTF-8', DOS: 'CP850';

# CPAN Modules
# use Excel::Writer::XLSX;
# perl -MCPAN -e "install Excel::Writer::XLSX"

my $s;
my @L;

my @ListOfFiles = <torben*.vcf>;
my %h;
foreach my $fileIn (@ListOfFiles) {
  open( my $fhIn, '<:encoding(UTF-8)', $fileIn )
      or die "ERROR: Can't read from file '$fileIn': $!";

  # binmode ($fhIn, ":encoding(UTF-8)");
  my $cont = join '', <$fhIn>;
  close $fhIn;
  $cont =~ s/\r\n/\n/g;    # EOL -> Linux

  # Neue Zeilen fangen so an: .*?(?=\n[A-Z]+[:;])

  # TODO: Foto wieder rein
  $cont =~ s/\nPHOTO;.*?(?=\n[A-Z]+[:;])//s
      ;    # Photo raus für einfacheres Debugging

  my @cards = split 'BEGIN:VCARD', $cont;
  shift @cards;
  say "" . ( $#cards + 1 ) . " cards";

  foreach my $card (@cards) {
    while ( $card =~ m/^([A-Z]+)[;:]/mgc ) {
      $h{$1}++;
    }
  }

  # by values, reverse
  foreach my $k ( sort { $h{$b} <=> $h{$a} } keys(%h) ) {

    # last if $h{$k}==1;
    print "$h{$k}\t$k\n";
  }
} ## end foreach my $fileIn (@ListOfFiles)
