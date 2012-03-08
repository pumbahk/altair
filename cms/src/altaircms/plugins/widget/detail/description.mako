<div class="description">
  ## todo refactoring(remove layout setting)
  ## todo performancesの表示する数を調整？

    <div style="TEXT-ALIGN: center">${h.base.nl_to_br(event.subtitle)|n}</div>
    <div style="TEXT-ALIGN: center"><font size="4" face="Arial, Verdana"><b>${h.base.nl_to_br(event.title)|n}</b></font></div>
	<div style="TEXT-ALIGN: left" align="left">${h.base.nl_to_br(event.description)|n}</div>
    <div style="TEXT-ALIGN: left" align="left">&nbsp;</div><font face="Arial, Verdana"><b>
    <div style="TEXT-ALIGN: left" align="left">&nbsp;</div><font face="Arial, Verdana"><b>
    <div style="TEXT-ALIGN: left" align="left"><strong>【公演日時・会場】</strong></div>
    <div style="TEXT-ALIGN: left" align="left">&nbsp;</div><font face="Arial, Verdana"><b>
    % for p in performances:
      <div style="TEXT-ALIGN: center" align="center" class="performances">
		## このサイズ指定は本当はcssでやるべき
		<font size="1">${h.event.performance_description(p)}</font>
	  </div>
    % endfor
    <br/>
    <br/>
</div>

<%doc>
<div class="description">
    <div style="TEXT-ALIGN: center"><font face="Arial, Verdana"><b><br></b></font></div>
    <div style="TEXT-ALIGN: center"><font size="3" face="Arial, Verdana"><b>アイフルホーム presents</b></font></div>
    <div style="TEXT-ALIGN: center"><strong><font size="3"></font></strong>&nbsp;</div><font face="Arial, Verdana">
      <div style="TEXT-ALIGN: center"><b><font size="4">松下奈緒コンサートツアー2012　for me</font></b></div>
      <div style="TEXT-ALIGN: center"><font size="4"></font>&nbsp;</div></font>
    <div style="TEXT-ALIGN: center"><font size="3" face="Arial, Verdana"><b>supported by ＪＡバンク</b></font></div>
    <div style="TEXT-ALIGN: center"><strong><font size="4"></font></strong>&nbsp;</div>
    <div style="TEXT-ALIGN: center"><strong><font size="4"></font></strong>&nbsp;</div>
    <div style="TEXT-ALIGN: center">&nbsp;</div>
    <div style="TEXT-ALIGN: center" align="left"><strong>【公演日時・会場】</strong></div>
    <div style="TEXT-ALIGN: center" align="left">&nbsp;</div><font face="Arial, Verdana"><b>
        <div style="TEXT-ALIGN: center"><font size="1">2012年6月3日（日）　16:30開場／17:00開演　岸和田市立浪切ホール　大ホール</font></div>
        <div style="TEXT-ALIGN: center"><font size="1">2012年7月16日（月・祝）　16:30開場／17:00開演　神戸国際会館こくさいホール<br></font></div></b></font>
    <div style="TEXT-ALIGN: left"><font face="Arial, Verdana"><b><br></b></font></div>
    <div style="TEXT-ALIGN: left"><font face="Arial, Verdana"><b><br></b></font></div>
</div>
</%doc>
