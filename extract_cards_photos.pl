#!/usr/bin/perl
use strict;
use warnings;
use 5.010;

# extract cards and photos from vcf addressbook file
# by Torben Menke http:/entorb.net

# Perl Standard Modules
use Data::Dumper;
use File::Basename;
use utf8;

# use open ":encoding(UTF-8)"; # for all files
use Encode;
my $encodingSay        = 'UTF-8';    # Linux: 'UTF-8', Windows: 'CP850';
my $encodingFileSystem = 'UTF-8';    # Linux: 'UTF-8', Windows: 'CP850';
use MIME::Base64;                    # for PHOTO extraction

my $s;
my @L;

my $fileIn = 'addressbook.vcf';
open( my $fhIn, '<:encoding(UTF-8)', $fileIn )
    or die encode $encodingSay, "ERROR: Can't read from file '$fileIn': $!";

# binmode ($fhIn, ":encoding(UTF-8)");

my $outputfolder = "extract_cards_photos";
mkdir $outputfolder unless -d $outputfolder;

my $cont = join '', <$fhIn>;
close $fhIn;

$cont =~ s/\r\n/\n/g;    # EOL -> Linux
@L = split /BEGIN:VCARD\n/, $cont;
undef $cont;
shift @L;                # remove first empty card

foreach my $vcard (@L) {
  $vcard = "BEGIN:VCARD\n$vcard";

  # extract contact name
  my $fn;
  if ( $vcard =~ m/^FN:(.*)\n/m ) {
    $fn = $1;
  }
  else {
    die encode $encodingSay, "ERROR: 'FN:' not found in card: \n'$vcard'\n";
  }
  $fn =~ s/\\,/,/g;
  $fn =~ s/[^\w ]+//g;    # remove /,\ and other non-word-chars

  my $fileOut = encode $encodingFileSystem, "$outputfolder/$fn.vcf";
  $fileOut =~ s/\?/_/g;    # remove unknown chars

  # Extract Photo
  my $photo;
  if ( $vcard =~ m/\nPHOTO[^:]*:(.*?)(?=\n[A-Z\-]+[:;])/s ) {
    $photo = $1;
    if ( defined($photo) ) {
      my $photoOut = $fileOut;
      $photoOut =~ s/\.vcf$/.jpg/;
      print $photoOut;
      my $photoDecoded = MIME::Base64::decode_base64($photo);
      open my $fhPhoto, '>', $photoOut or die $!;
      binmode $fhPhoto;
      print $fhPhoto $photoDecoded;
      close $fhPhoto;
    } ## end if ( defined($photo) )
  } ## end if ( $vcard =~ m/\nPHOTO[^:]*:(.*?)(?=\n[A-Z\-]+[:;])/s)

  open( my $fhOut, '>:encoding(UTF-8)', $fileOut )
      or
      die( encode $encodingSay, "ERROR: Can't write to file '$fileOut': $!" );

  # binmode ($fhOut, ":encoding(UTF-8)");
  print $fhOut $vcard;
  close $fhOut;
}    # foreach my $vcard (@L) {
