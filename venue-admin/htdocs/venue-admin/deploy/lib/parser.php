<?php
/*
	P-strain Template Engine
	
	Author: SASAO Takahiro <sasao@p-strain.jp>
*/
class Parser {
	var $object;
	var $html_version = 'HTML';
	
	var $count = array();
	
	var $loader = null;
	
	private function attr2hash($str) {
		$hash = array();
		while(preg_match('/^(.*\s|)([^"\s]+)="([^"]*)"(.*)$/', $str, $m)) {
			$hash[$m[2]] = $m[3];
			$str = $m[1].$m[4];
		}
		return $hash;
	}
	
	function parse($template, &$data, $return = FALSE) {
		// TODO:
		// 漢字コード自動制御 or 手動制御
		// UTF-8だけを扱うことを想定
		
		while(preg_match('{^(.*)<template:import([^>]+)/>(.*)$}s', $template, $m)) {
			$opt = $this->attr2hash($m[2]);
			$loaded = "";
			if(is_array($this->loader)) {
				$loaded = call_user_func($this->loader, $opt);
				$template = $m[1].$loaded.$m[3];
			}
		}
		
		// テンプレートを連想配列に分解する
		$blocks = preg_split('{(</?template:(?:block|tag)[^>]*>)}', $template, -1, PREG_SPLIT_DELIM_CAPTURE);
		$sections = array(":0");
		$struct = array(":0" => "");
		$seq = 0;
		while(0 < count($blocks) && 0 < count($sections)) {
			$section = $sections[0];
			$struct[$section] .= array_shift($blocks);
			
			if(0 < count($blocks)) {
				$tag = array_shift($blocks);
				if(substr($tag, 1, 1) == "/") {
					// close tag
					array_shift($sections);
				} else {
					// open tag
					// ブロックは、${@ID:seq}に置き換える
					if(preg_match('/id="([^"]*)"/', $tag, $matches)) {
						$id = $matches[1];
					} else {
						$id = "_";
					}
					$seq++;
					$struct[$section] .= '${@'."$id:".($seq).'}';
					$struct["$id:".($seq)] = "";
					$struct["$id:".($seq).":type"] = preg_replace('/^<template:(block|tag).+$/', '$1', $tag);
					if(preg_match('/mode="([^"]+)"/', $tag, $matches)) {
						$struct["$id:".($seq).":mode"] = $matches[1];
					}
					if(preg_match('/where="([^"=]*?)(!=|=)([^"=]*)"/', $tag, $matches)) {
						$struct["$id:".($seq).":where"] = array($matches[1], $matches[3], $matches[2]);
					}
					array_unshift($sections, "$id:".($seq));
				}
			}
		}
	//	print "<XMP>";print_r($struct);exit;
		
		// マクロ展開する
		$output = preg_replace('/\${([^}]*)}/eS', '$this->macro(\'$1\', \$data, \$struct)', $struct[":0"]);
		
		// 3rd paramがTRUEの場合、final_outputにセットしない
		// この仕様と動作はview($template, $data, $return)と同様
		if($return == FALSE) {
			header('Content-Type: text/html; charset=UTF-8');
			print $output;
		}
		return $output;
	}
	
	// マクロ展開
	// ${...}内のマクロ命令、データ、テンプレートを受け取って、単一文字列を返す
	// const $data
	// const $struct
	function macro($macro, &$data, &$struct) {
		// \" -> " 変換
		// ref. http://www.php.net/manual/ja/function.preg-replace.php#39713
		$macro = str_replace('\"', '"', $macro);
		
		if(preg_match('/^@(.*):(\d+)$/', $macro, $matches)) {
			// ブロックがあったところ
			list($section, $seq) = array($matches[1], $matches[2]);
			if(!isset($struct["$section:$seq"])) {
				// 内部エラー
				return "";
			}
			$template =& $struct["$section:$seq"];
			$buf = array();
			$morebuf = array();
			if($struct["$section:$seq:type"] == 'tag') {
				$ds = array(array());
				if(isset($data[$section]) && is_array($data[$section]) && isset($data[$section]["tag"])) {
					$buf[] = '<'.$data[$section]["tag"].(empty($data[$section]["attr"]) ? '' : ' '.$data[$section]["attr"]).'>';
					$morebuf[] = '</'.$data[$section]["tag"].'>';
				}
			} elseif(is_array($data) && isset($data[$section]) && is_array($data[$section])) {
				$ds =& $data[$section];
			} elseif(is_object($data) && isset($data->$section) && is_array($data->$section)) {
				$ds =& $data->$section;
			} else {
				$ds = array(array());
			}
			$counter = 0;
			foreach($ds as $idx => $d) {
				// TODO: parent修飾子が使えたりする方がよいかも
				// FIXME: $dがarrayじゃない場合に落ちる
				if(is_object($d)) {
					$d = (array) $d;
				}
				if(is_array($d)) {
					if(is_array($data)) {
						// マージする(既に存在するkeyは上書きされない)
						#$d += $data;
						foreach($data as $k => $v) {
							if(!array_key_exists($k, $d)) {
								$d[$k] =& $data[$k];
							}
						}
					} elseif(is_object($data)) {
						foreach($data as $k => $v) {
							if(!array_key_exists($k, $d)) {
								$d[$k] =& $data[$k];
							}
						}
					}
				}
				if(isset($struct["$section:$seq:where"])) {
					$copy_d = $d;
					$dummy_s = array();
					$where_op = $struct["$section:$seq:where"][2];
					$where_l = preg_replace('/\${([^}]*)}/eS', '$this->macro(\'$1\', \$copy_d, \$dummy_s)', $struct["$section:$seq:where"][0]);
					$where_r = preg_replace('/\${([^}]*)}/eS', '$this->macro(\'$1\', \$copy_d, \$dummy_s)', $struct["$section:$seq:where"][1]);
					if($where_op == '=' && $where_l !== $where_r) {
						continue;
					}
					if($where_op == '!=' && $where_l === $where_r) {
						continue;
					}
				}
				$d["$section idx"] = $counter;
				if(isset($d[' idx'])) {
					unset($d[' idx']);
				}
				$d[' idx'] = $counter++;;
				$buf[] = preg_replace('/\${([^}]*)}/eS', '$this->macro(\'$1\', \$d, \$struct)', $template);
			}
			if(isset($struct["$section:$seq:mode"]) && $struct["$section:$seq:mode"] == 'hidden') {
				return '';
			}
			return join('', $buf) . join('', $morebuf);
		} else {
			# /.../S あるパターンを複数回使用する場合は、マッチングにかかる時間を高速化することを目的として、
			# パターンの分析に幾分か時間をかけても良いでしょう。この修飾子を設定すると、追加のパターン分析が
			# 行われます。現在、パターン分析は、最初の文字が単一ではなく、かつ固定でないパターンに対してのみ
			# 有用です。
			
			# data.func(arg).func(arg)
			# ただしargには`)'を含められない.
			
			if(preg_match('/^([^\(\)]*)((\.[^\(\.]+(\([^\)]*\))?)*)$/S', $macro, $m)) {
			#                 name.e*   .func      (args   )
				if($m[1] === "") {
					$names = array($m[1]);
					$macro = $m[2];
					$value = $data;
				} else {
					$names = explode('.', $m[1]);
					$macro = $m[2];
					$d =& $data;
					foreach($names as $n) {
						if(is_array($d) && isset($d[$n])) {
							$d2 =& $d[$n];
							unset($d);
							$d =& $d2;
						} elseif(is_object($d) && isset($d->$n)) {
							$d2 =& $d->$n;
							unset($d);
							$d =& $d2;
						} else {
							unset($d);
							$d = '';
							break;
						}
					}
					$value = $d;
					unset($d);
				}
			} else {
				return '';
			}
			
			// ループで処理するのも悪くは無いが、
			// スタックにして、再帰処理する方が柔軟性が高いと思う.
			
			if(preg_match_all('/\.([^\(\.]+)(?:\(([^\)]*)\))?/S', $macro, $m, PREG_SET_ORDER)) {
			#                    . func~~~~     ( args~~  )
				foreach($m as $funcargs) {
					$func = $funcargs[1];
					$args = isset($funcargs[2]) ? $funcargs[2] : null;
					
					$out = $this->process_func($func, $args, $value, $data, $names[0]);
					
					if(!is_array($value) && is_array($out)) {
						// 一部のマクロは、HTMLタグを出力する
						// エスケープせずに処理を打ち切り、後続処理は認めない
						return isset($out[0]) ? $out[0] : null;
					}
					$value = $out;
				}
			}
			
			if(is_array($value) && isset($value[0]) && !is_array($value[0])) {
				return $value[0];
			}
			
			return $this->escape($value);
		}
	}
	
	function single_tag($tag, $attrs) {
		if($this->html_version == 'XHTML') {
			return sprintf('<%s %s />', $tag, $attrs);
		} else {
			return sprintf('<%s %s>', $tag, $attrs);
		}
	}
	
	var $dateFormat = array(
		'date' => 'MM/DD/YYYY',
		'datetime' => 'MM/DD/YYYY hh:mm:ss',
	);
	
	function to_japanese_year($y, $m=1, $d=1, $use_kanji=1) {
		if($use_kanji) {
			$nengo = array('', '明治','大正','昭和','平成');
		} else {
			$nengo = array('', 'M', 'T', 'S', 'H');
		}
		$ymd = 1*sprintf('%04u%02u%02u', $y, $m, $d);
		if(19890108 <= $ymd) {
			$jy = $nengo[4].($y-1988);
		} elseif(19261225 <= $ymd) {
			$jy = $nengo[3].($y-1925);
		} elseif(19120730 <= $ymd) {
			$jy = $nengo[2].($y-1911);
		} elseif(18680908 <= $ymd) {
			$jy = $nengo[1].($y-1867);
		} else {
			return $y;
		}
	//	if($use_kanji) {
	//		return preg_replace('/^([^\d]+)1$/', "$1元", $jy);
	//	}
		return $jy;
	}
	
	function process_func($func, $args, $value, &$data, $name) {
		$num_re = '/^-?[\d\.]+$/';
		if($func == 'format') {
			$value = trim($this->to_string($value));
			if(isset($this->dateFormat[$args])) {
				$args = $this->dateFormat[$args];
			}
			if(strpos($args, '%') !== FALSE) {
				// %.2fとか%uとかは四捨五入じゃなくて切り捨てであることに注意
				return is_numeric($value) ? array(sprintf($args, $value)) : $value;
			} elseif(preg_match('/^(\d{4})$/', $value, $p)
			|| preg_match('/^(\d+)\D+(\d+)\D+(\d+)(\s+(\d+):(\d+)(:(\d+))?(\.\d+)?)?$/', $value, $p)
			|| preg_match('/^(\d+)\D+(\d+)\D+(\d+)(T(\d+):(\d+)(:(\d+))([\+-]\d+:00)?)$/', $value, $p)) {
				$t = array();
				$t['YYYY'] = sprintf('%04u', $p[1]);
				$t['YY'] = sprintf('%02u', $p[1]%100);	$t['Y'] = $p[1]*1;
				$t['J'] = $this->to_japanese_year($p[1], 1, 1, 1);
				$t['j'] = $this->to_japanese_year($p[1], 1, 1, 0);
				if(3 <= count($p)) {
					$t['MMMM'] = chr(1);   # 月名フルスペル
					$t['MMMm'] = chr(2);   # 月名略語+.(Mayを除く)
					$t['MMM'] = chr(3);   # 月明略語(.無し)
					$t['MM'] = sprintf('%02u', $p[2]);	$t['M'] = $p[2]*1;
					$t['DD'] = sprintf('%02u', $p[3]);	$t['D'] = $p[3]*1;
					$t['w'] = date('w', mktime(0, 0, 0, $p[2], $p[3], $p[1]));
					$dow = array('日', '月', '火', '水', '木', '金', '土');
					$t['W'] = $dow[date('w', mktime(0, 0, 0, $p[2], $p[3], $p[1]))];
					$t['J'] = $this->to_japanese_year($p[1], $p[2], $p[3], 1);
					$t['j'] = $this->to_japanese_year($p[1], $p[2], $p[3], 0);
					if(7 <= count($p)) {
						$t['hh'] = sprintf('%02u', $p[5]);	$t['h'] = $p[5]*1;
						$t['mm'] = sprintf('%02u', $p[6]);	$t['m'] = $p[6]*1;
					}
					if(8 <= count($p)) {
						$t['ss'] = sprintf('%02u', $p[8]);	$t['s'] = $p[8]*1;
					}
					$t[chr(1)] = date('F', mktime(0, 0, 0, $p[2], 1, 2000));
					$t[chr(2)] = date('M', mktime(0, 0, 0, $p[2], 1, 2000)).($p[2]!='5'?'.':'');
					$t[chr(3)] = date('M', mktime(0, 0, 0, $p[2], 1, 2000));
				}
				return array(str_replace(array_keys($t), array_values($t), $args));
			} elseif(!$value) {
				return $value;
			} else {
				return "invalid[$value]";
			}
		} elseif($func == 'signed') {
			$value = $this->to_string($value);
			if(preg_match($num_re, $value)) {
				return (0 < "$value"*1) ? '+'.$value : "$value";
			}
		} elseif($func == 'plus') {
			$value = $this->to_string($value);
			if(preg_match($num_re, $value) && preg_match($num_re, $args)) {
				return "$value"*1 + "$args"*1;
			}
		} elseif($func == 'div') {
			$value = $this->to_string($value);
			if(preg_match($num_re, $value) && preg_match($num_re, $args)) {
				return "$value" / "$args";
			}
		} elseif($func == 'mul') {
			$value = $this->to_string($value);
			if(preg_match($num_re, $value) && preg_match($num_re, $args)) {
				// SimpleXMLElement対策
				return "$value" * "$args";
			}
		} elseif($func == 'round') {
			$value = $this->to_string($value);
			if(preg_match('/^-?\d+(\.\d+)?$/', $value)) {
				$value = trim($value) * 1;
				return $args ? round($value, $args) : round($value);
			} else {
				return $value;
			}
		} elseif($func == 'left') {
			$value = $this->to_string($value);
			return substr($value, 0, $args*1);
		} elseif($func == 'hidden') {	// htmlタグを返す
			return array($this->single_tag('input',
					sprintf('type="hidden" name="%s" value="%s"', $name, $this->escape($value))
			));
		} elseif($func == 'if') {	// booleanを返す
			$value = $this->to_string($value);
			$reverse = 0;
			if(substr($args, 0, 1) == '!') {	// 否定
				$args = substr($args, 1);
				$reverse = 1;
			}
			if(substr($args, 0, 1) == '=') {	// 文字列マッチ
				if(!is_array($value)) {
					$result = strcmp($value, substr($args, 1))==0 ? 1 : 0;
					return $reverse ? 1-$result : $result;
				} else {
					return 0;
				}
			} elseif(substr($args, 0, 1) == '|') {	// 含まれる
				if(is_array($value)) {
					$result = in_array(substr($args, 1), $value) ? 1 : 0;
				} elseif(0 < strlen($value)) {
					$result = strpos($value, substr($args, 1))!==FALSE ? 1 : 0;
				} else {
					$result = 0;
				}
				return $reverse ? 1-$result : $result;
			} else {	// 演算子無し
				$result = ($value == $args) ? 1 : 0;
				return $reverse ? 1-$result : $result;
			}
		} elseif($func == 'then') {		// valueは使わずargsを出力する
			$value = $this->to_string($value);
			if($value) {
				return array($args);
			} else {
				return "";
			}
		} elseif($func == 'else') {		// valueは使わずargsを出力する
			$value = $this->to_string($value);
			if(!$value) {
				return array($args);
			} else {
				return "";
			}
		} elseif($func == 'not') {
			$value = $this->to_string($value);
			return $value ? '' : 1;
		} elseif($func == 'option') {
			$value = $this->to_string($value);
			if($value == $args) {
				return array(sprintf('value="%s" selected="selected"', $args));
			} else {
				return array(sprintf('value="%s"', $args));
			}
		} elseif($func == 'trim') {
			$value = $this->to_string($value);
			return mb_strimwidth($value, 0, 1*$args, "...");
		} elseif($func == 'selected' || $func == 'checked') {
			$value = $this->to_string($value);
			// パラメータが空文字列の場合は、任意のデータがあれば有効
			if(($args == '' && $value) || ($args != '' && $value == $args)) {
				return array(sprintf('%s="%s"', $func, $func));
			} else {
				return '';
			}
		} elseif($func == 'nonl') {
			$value = $this->to_string($value);
			return str_replace("\n", " ", $value);
		} elseif($func == 'nl2br') {
			$value = $this->to_string($value);
			return array(nl2br($this->escape($value)));
		} elseif($func == 'html') {
			// 何もせずにそのままHTMLを通過させる(細心の注意をもって使用すべき)
			$value = $this->to_string($value);
			return array($value);
		} elseif($func == 'comma') {
			$value = trim($this->to_string($value));
			if(preg_match('/^(-?[\D]*\d{1,3})((\d{3})+)((\.\d+)?)$/', $value, $m)) {
				return $m[1] . preg_replace('/(...)/', ',$1', $m[2]) . $m[4];
			}
			return $value;
		} elseif($func == 'uri') {
			$value = $this->to_string($value);
			return urlencode($value);
		} elseif($func == 'quote') {
			$value = $this->to_string($value);
			// for javascript
			// イベントハンドラ中では、これをそのまま使う(html escapeも行われる)
			// script要素中では、</script>が登場してしまうとまずいことになるので
			// 特殊な処理を行う.
			// ref W3C HTML4.01仕様 B.3.2
			// see http://d.hatena.ne.jp/ockeghem/20070511/1178899191
			if($args == 's') {
				// (HTML属性のイベントハンドラで) シングルクォートで囲む
				return "'".addslashes($value)."'";
			} elseif($args == '"') {
				// (HTML属性のイベントハンドラで) シングルクォートで囲む
				return "'".addslashes($value)."'";
			} elseif($args == 'csv') {
				return '"'.str_replace('"', '""', $value).'"';
			} elseif($args == 'script') {
				// SCRIPT要素中で、シングルクォートで囲む
				$yen = '\\';
				$convert = array($yen => $yen.$yen, '<' => $yen.'x3c', '>' => $yen.'x3e', '"' => $yen.'"', "'" => $yen."'");
				return array("'".str_replace(array_keys($convert), array_values($convert), $value)."'");	// no html escape
			} else {	// モードsと同じ処理
				// (HTML属性のイベントハンドラで) シングルクォートで囲む
				return "'".addslashes($value)."'";
			}
		} elseif($func == 'dump') {
			ob_start();
				var_dump($value);
			return array(ob_get_clean());
		} elseif($func == 'element') {
			if(is_array($value) && is_numeric($args) && $args < 0) {
				$args = count($value) + $args;
			}
			if(is_array($value) && isset($value[$args])) {
				$value = $value[$args];
			} elseif(is_object($value) && isset($value->$args)) {
				$value = $value->$args;
			} elseif(!is_array($value)) {
				;
			} else {
				$value = "";
			}
		} elseif($func == 'shift') {
			if(isset($data[$name]) && is_array($data[$name]) && isset($data[$name][0])) {
				return array_shift($data[$name]);
			} else {
				return "[cannot shift $name]";
			}
		} elseif($func == 'pop') {
			if(isset($data[$name]) && is_array($data[$name]) && isset($data[$name][0])) {
				return array_pop($data[$name]);
			} else {
				return "[cannot pop $name]";
			}
		} elseif($func == 'delete') {
			if(isset($value[$args])) {
				unset($value[$args]);
			}
		} elseif($func == 'query') {
			if(is_array($value)) {
				$value = http_build_query($value);
				return $value ? "?$value&" : "?";
			}
			return '';
//		} elseif($func == 'query-stringをhashにするようなのが欲しい') {
		} elseif($func == 'index') {
			if(isset($value[' idx'])) {
				return $value[' idx'];
			} else {
				return '';
			}
		} elseif($func == 'count') {
			if(is_array($value)) {
				return count($value);
			}
		} elseif($func == 'current') {
			if(isset($data["$name idx"]) && isset($value[$data["$name idx"]])) {
				return $value[$data["$name idx"]];
			}
		}
		return $value;
	}
	
	function escape($str, $opt=ENT_QUOTES, $encoding=false, $auto_shift=true) {
		// ENT_QUOTES for convert both " and '
		// ENT_COMPAT for convert only " then leave '
		// ENT_NOQUOTES for leave both " and '
		if($encoding === false) {
			$encoding = 'UTF-8';
		}
		
		if($auto_shift) {
			$str = $this->to_string($str);
		}
		
		return htmlspecialchars($str, $opt, $encoding);
	}
	
	function to_string($a) {
		// 多次元配列は、最初の要素だけを取り出す
		while(is_array($a)) {
			if(isset($a[''])) {
				$a = $a[''];
			} elseif(isset($a[0])) {
				$a = $a[0];
			} else {
				$a = array_shift($a);
			}
		}
		return $a;
	}
}
