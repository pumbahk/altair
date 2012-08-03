package QR;

# FIXME: 名前がナンセンスなので本当に使うなら要修正

use strict;

use utf8;
use Encode;

sub new {
	my $class = shift;
	my $opt = shift;
	
	bless $opt, $class;
}

# 長さを前置するなら、各ビットを使いきっていいのだが現状は混在してる

# 0-31 int -> char
my @c32 = split(//, '0123456789ABCDEFGHIJKLMNOPQRSTUV');
my %c32_2i = map { $c32[$_], $_ } (0 .. $#c32);

# @private
sub c32 {
	my $i = shift;
	die "$i is out of range." unless(0 <= $i && $i < 32);
	$c32[$i];
}

# [4bit][4bit]...[4bit|16]
# @private
sub c32m {
	my $i = shift;
	my $len = shift;
	my @result = ();
	while(1) {
		unshift(@result, c32($i % 16 + ($#result==-1?16:0)));
		if($i < 16) {
			last;
		} else {
			$i = int($i/16);
		}
	}
	die "too large: $i" if(0 < $len && $len < $#result+1);
	while($#result+1 < $len) {
		unshift(@result, '0');
	}
	join('', @result);
}

# @private
sub decode_c32m {
	my $str = shift;
	
	my $n = 0;
	foreach my $c (split(//, $str)) {
		my $int = $c32_2i{$c};
		$n = $n*16 + ($int%16);
	}
	$n;
}

# [\xa1-\xfe][\xa1-\xfe] -> [$%*+/][$..Z][$..Z]
my @c42 = split(//, '$%*+/.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ');
my %c42_2i = map { $c42[$_], $_ } (0 .. $#c42);
# @private
sub enc42 {
	my $c = shift;		# euc-jp string
	
	my @idx = unpack('C*', $c);
	die "out of range: ".join(" ", map { sprintf('%02x', $_) } @idx)
		unless($#idx==1 && 160<=$idx[0] && 160<=$idx[1]);
	my $idx = ($idx[0]-160)*96+($idx[1]-160);
	my @abc = (int($idx / 42 / 42), int($idx / 42) % 42, $idx % 42);
	
	die "out of range: $idx" if(5 < $abc[0]);
	
	join("", map { $c42[$_] } @abc);
}

# mixed conveter
# @private
sub encode42 {
	my $str = shift;
	
	if(!utf8::is_utf8($str)) {
		$str = Encode::decode('utf-8', $str);
	}
	$str = Encode::encode('euc-jp', $str);
	
	my $result = "";
	while($str =~ s/^([\x80-\xfe][\x80-\xfe]|[0-9A-Z: -])//) {
		my $c = $1;
		if($c =~ /^[\x80-\xfe]/) {
			$result .= enc42($c);
		} else {
			$result .= $c;
		}
	}
	$result;
}

# @private
sub decode42 {
	my $str = shift;
	
	my @result = ();
	while($str =~ s{^([\$%*\+/][\$%*\+/\.0-9A-Z]{2}|[0-9A-Z: -])}{}) {
		my $token = $1;
		if(length($token) == 1) {
			push(@result, $token);
		} elsif(length($token) == 3) {
			my($a, $b, $c) = split(//, $token);
			my $n = ($c42_2i{$a}*42+$c42_2i{$b})*42+$c42_2i{$c};
			push(@result, pack('C*', int($n/96)+160, $n%96+160));
		}
	}
	Encode::decode('euc-jp', join('', @result));
}

# 5 byte binary -> 8 characters
# @private
sub encode_bin {
	my $bin = shift;
	
	$bin =~ s{(.)(.)(.)(.)(.)}{
		c32((ord($1)&0xf8)>>3).
		c32((ord($1)&0x07)<<2 | (ord($2)&0xc0)>>6).
		c32((ord($2)&0x3e)>>1).
		c32((ord($2)&0x01)<<4 | (ord($3)&0xf0)>>4).
		c32((ord($3)&0x0f)<<1 | (ord($4)&0x80)>>7).
		c32((ord($4)&0x7c)>>2).
		c32((ord($4)&0x03)<<3 | (ord($5)&0xe0)>>5).
		c32((ord($5)&0x1f))
	}eg;
	$bin;
}

my $signlen = 8;

use Digest::SHA1 qw(sha1);
sub sign {
	my $self = shift;
	my $body = shift;
	my $key = $self->{key};
	
	substr(encode_bin(sha1($body.$key)), 0, $signlen) . $body;
}

sub check {
	my $self = shift;
	my $signbody = shift;
	
	my $sign = substr($signbody, 0, $signlen);
	my $body = substr($signbody, $signlen);
	
	$self->sign($body) == $sign;
}

my $tags = {
	serial => 1,			# variable length [code]
	order => 10,			# variable length [code]
	performance => 11,		# variable length [code]
	date => 12,				# 4chars
	type => 13,				# variable length [int]
	seat => 14,				# variable length [str]
};

# not support structured data
sub make_data {
	my $self = shift;
	my $hash = shift;
	
	my @buffer = ();
	my $add_code = sub {
		my $tag = shift;
		my $content = shift;
		die "unsupported tag: $tag" unless(defined $tags->{$tag});
		push(@buffer, c32m($tags->{$tag}).c32m(length($content)).$content);
	};
	
	&$add_code('serial', $hash->{serial});
	&$add_code('performance', $hash->{performance});
	&$add_code('order', $hash->{order});
	
	my @ymd = ($hash->{date} =~ /^(\d\d\d\d)(\d\d)(\d\d)$/);
	my $date = c32m($ymd[0] - 2000, 2).c32($ymd[1]*1).c32($ymd[2]*1);
	$date =~ /^[0-9A-Z]{4}$/ or die;	# 4 chars
	&$add_code('date', $date);
	
	&$add_code('type', c32m($hash->{type}));
	
	&$add_code('seat', encode42($hash->{seat}));
	
	join('', @buffer);
}

# @private
sub parse_data {
	my $str = shift;
	
	my $read_int = sub {
		my $i = 0;
		while($str =~ s/^(.)//) {
			if(16 <= $c32_2i{$1}) {
				return $i*16 + $c32_2i{$1} - 16;
			} else {
				$i = $i*16 + $c32_2i{$1};
			}
		}
	};
	
	my %i2tag = map { $tags->{$_}, $_ } (keys %$tags);
	
	my %result = ();
	while(2 <= length($str)) {
		my $tag = &$read_int();
		my $len = &$read_int();
		my $data = substr($str, 0, $len);
		$str = substr($str, $len);
		
		# typeによって型が異なる...
		my $mode = 'raw';
		$mode = 'int' if($i2tag{$tag} eq 'type');
		$mode = 'str' if($i2tag{$tag} eq 'seat');
		
		$data = decode_c32m($data) if($mode eq 'int');
		$data = decode42($data) if($mode eq 'str');
		
		$result{$i2tag{$tag}} = $data;
	}
	
	\%result;
}

sub parse_signed_data {
	my $self = shift;
	my $signed = shift;
	
	if($self->check($signed)) {
		parse_data(substr($signed, $signlen));
	} else {
		die "maybe broken.";
	}
}

1;
