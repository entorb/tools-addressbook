#!/bin/perl -w
# reads a vcf addressbook file
# exports a copy containing only cards having a bday

# Modules: My Default Set
use strict;
use warnings;

use 5.010;
use utf8;    # this script is written in UTF-8
use autodie
    ;    # Replace functions with ones that succeed or die with lexical scope

# use Data::Dumper;

# Modules: Perl Standard
use Time::Local;

# Encoding
use Encode qw(encode decode);

# use open ':encoding(UTF-8)';    # default encoding for all files, not working for open( my $fhIn, '<', $fileIn )
# default encoding for print STDOUT
if ( $^O eq 'MSWin32' ) {
  binmode( STDOUT, ':encoding(cp850)' );
}
else {
  binmode( STDOUT, ':encoding(UTF-8)' );
}

# Modules: File Access
use File::Basename;

# TODO: enter your data
my $fileIn = 'ab.vcf';

# chdir to dir of perl file
chdir dirname(__FILE__);

# whiteliste of fields to keep
my $fieldsAllowed = join '|', qw ( BEGIN END BDAY N );

my @cont;
open( my $fhIn, '<:encoding(UTF-8)', $fileIn ) or die $!;

# whilelist of only lines that start with one of the allowed keywords. (these must be single-line-keywords)
# @cont = grep {m/^($fieldsAllowed)[:;].*/} <$fhIn>;
while ( my $line = <$fhIn> ) {
  next if not $line =~ m/^($fieldsAllowed)[:;].*/;
  $line             =~ s/\r\n$/\n/;    #Linebreaks; Windows -> Linux
  push @cont, $line;
}

# say $#cont;
close $fhIn;

# filter to only cards having bdays
my @cards = split m/BEGIN:VCARD/, join( '', @cont );
undef @cont;
@cards = grep {m/\nBDAY[;:]/} @cards;

if ( $#cards > 0 ) {

  # export addressbook of only birthdays
  my ( $fname, $fdir, $fext ) = fileparse( $fileIn, qr/[.][^.]*/ );
  my $fileOut = "$fname-BdayOnly$fext";
  open( my $fhout, '>', $fileOut ) or die $!;
  print {$fhout} 'BEGIN:VCARD' . join 'BEGIN:VCARD', @cards;
  close $fhout;
} ## end if ( $#cards > 0 )

1;
