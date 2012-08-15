use strict;
use utf8;
use lib 'lib';
use QR;

my $qr = new QR({
	key => 'ticketstar',
});

my $data = $qr->make_data({
	serial => 'SERIALNUMBER',
	performance => 'PERFORMANCE',
	order => 'ORDERNUMBER',
	date => '20120805',
	type => 666,
	seat => 'ポンチョ席-A列-10'
});

my $signed = $qr->sign($data);

print "signed: ", $signed, "\n";
print "len: ", length($signed), "\n";

use YAML;
binmode STDOUT => ':encoding(utf-8)';
print Dump $qr->parse_signed_data($signed);

# 5dot, version=8[20mm], H correction -- max 122 chars

1;
