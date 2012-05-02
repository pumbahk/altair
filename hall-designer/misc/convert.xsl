<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:svg="http://www.w3.org/2000/svg"
    xmlns:meta="http://xmlns.ticketstar.jp/2012/venue-meta"
    version="1.0">

  <!-- override default template -->
  <xsl:template match="text()" />

  <!-- get the first chunk delimited by the specified string in the string -->
  <xsl:template name="get-first-chunk">
    <xsl:param name="value" />
    <xsl:param name="delimiter" select="','" />
    <xsl:variable name="possibly-delimited" select="normalize-space(substring-before($value, $delimiter))" />
    <xsl:choose>
      <xsl:when test="$possibly-delimited">
        <xsl:value-of select="$possibly-delimited" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="normalize-space($value)" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <!-- get all the chunks after the first delimited by the specified string in the string -->
  <xsl:template name="following-chunks">
    <xsl:param name="value" />
    <xsl:param name="delimiter" select="','" />
    <xsl:variable name="possibly-delimited" select="normalize-space(substring-after($value, $delimiter))" />
    <xsl:choose>
      <xsl:when test="$possibly-delimited">
        <xsl:value-of select="$possibly-delimited" />
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="''" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="rgba-value-as-rgb">
    <xsl:param name="value" />
    <xsl:text>rgb(</xsl:text>
    <xsl:variable name="c0">
      <xsl:call-template name="get-first-chunk"><xsl:with-param name="value" select="$value" /></xsl:call-template>
    </xsl:variable>
    <xsl:variable name="after-0">
      <xsl:call-template name="following-chunks"><xsl:with-param name="value" select="$value" /></xsl:call-template>
    </xsl:variable>
    <xsl:variable name="c1">
      <xsl:call-template name="get-first-chunk"><xsl:with-param name="value" select="$after-0" /></xsl:call-template>
    </xsl:variable>
    <xsl:variable name="after-1">
      <xsl:call-template name="following-chunks"><xsl:with-param name="value" select="$after-0" /></xsl:call-template>
    </xsl:variable>
    <xsl:variable name="c2">
      <xsl:call-template name="get-first-chunk"><xsl:with-param name="value" select="$after-1" /></xsl:call-template>
    </xsl:variable>
    <xsl:value-of select="concat($c0, ', ', $c1, ', ', $c2)" />
    <xsl:text>)</xsl:text>
  </xsl:template>

  <!-- parses appearances styles -->
  <xsl:template name="parse-appearance-styles">
    <xsl:param name="class-name" />
.<xsl:value-of select="$class-name" /> {
<xsl:if test="RenderAttribute/Body">    fill: <xsl:call-template name="rgba-value-as-rgb"><xsl:with-param name="value" select="RenderAttribute/Body/@color" /></xsl:call-template>;
</xsl:if>
  <!-- <xsl:if test="RenderAttribute/Frame">    stroke-width: <xsl:value-of select="RenderAttribute/Frame/@width" />px;
    stroke: <xsl:call-template name="rgba-value-as-rgb"><xsl:with-param name="value" select="RenderAttribute/Frame/@color" /></xsl:call-template>;
</xsl:if> -->
    stroke-width: 20px;
    stroke: rgb(0,0,0);
  <xsl:if test="FontAttribute/@color">    color: rgb(<xsl:value-of select="FontAttribute/@color" />);
</xsl:if>
  <xsl:if test="FontAttribute/@size">    font-size: <xsl:value-of select="FontAttribute/@size" />pt;
</xsl:if>
  <xsl:if test="FontAttribute/@style">    font-weight: <xsl:value-of select="FontAttribute/@style" />;
</xsl:if>}
</xsl:template>

  <!-- converts pairs of points into a series of SVG commands -->
  <xsl:template name="convert-pairs-to-svg-path-data">
    <xsl:param name="value" />
    <xsl:param name="command" select="'L'" />
    <xsl:variable name="first-chunk" select="normalize-space(substring-before($value, ','))" />
    <xsl:variable name="remainder" select="normalize-space(substring-after($value, ','))" />
      <xsl:value-of select="$command" /><xsl:text> </xsl:text><xsl:value-of select="number($first-chunk)" /><xsl:text> </xsl:text><xsl:choose>
      <xsl:when test="contains($remainder, ',')">
        <xsl:value-of select="number(normalize-space(substring-before($remainder, ',')))" /><xsl:text> </xsl:text>
        <xsl:call-template name="convert-pairs-to-svg-path-data"><xsl:with-param name="value" select="normalize-space(substring-after($remainder, ','))" /></xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="number(normalize-space($remainder))" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="/Hall">
    <xsl:variable name="width" select="number(substring-before(InitialViewStatus/Center, ',')) * 4" />
    <xsl:variable name="height" select="number(substring-after(InitialViewStatus/Center, ',')) * 6" />
    <svg:svg version="1.1" viewBox="0 0 {$width} {$height}" preserveAspectRatio="xMinYMin slice">
      <meta:description>
        <meta:gettii-id><xsl:value-of select="ID" /></meta:gettii-id>
        <meta:name><xsl:value-of select="Name" /></meta:name>
      </meta:description>
      <svg:style type="text/css">
        <xsl:apply-templates select="BlockLayerAttribute|GateLayerAttribute|RowLayerAttribute|SeatLayerAttribute" mode="css" />
      </svg:style>
      <xsl:apply-templates select="BlockLayers" />
    </svg:svg>
  </xsl:template>

  <xsl:template match="BlockLayerAttribute[@visible='true']" mode="css">
    <xsl:call-template name="parse-appearance-styles">
      <xsl:with-param name="class-name" select="'block'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="GateLayerAttribute[@visible='true']" mode="css">
    <xsl:call-template name="parse-appearance-styles">
      <xsl:with-param name="class-name" select="'gate'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="RowLayerAttribute[@visible='true']" mode="css">
    <xsl:call-template name="parse-appearance-styles">
      <xsl:with-param name="class-name" select="'row'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="SeatLayerAttribute[@visible='true']" mode="css">
    <xsl:call-template name="parse-appearance-styles">
      <xsl:with-param name="class-name" select="'seat'" />
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="BlockLayers">
    <xsl:apply-templates select="BlockLayer" />
  </xsl:template>

  <xsl:template match="BlockLayer">
    <xsl:choose>
      <xsl:when test="@positions">
        <xsl:variable name="path-data">
          <xsl:call-template name="convert-pairs-to-svg-path-data">
            <xsl:with-param name="value" select="@positions" />
            <xsl:with-param name="command" select="'M'" />
          </xsl:call-template>
        </xsl:variable>
        <svg:path d="{$path-data}" class="block" />
      </xsl:when>
      <xsl:when test="@position">
        <svg:rect x="{normalize-space(substring-before(@position, ','))}" y="{normalize-space(substring-after(@position, ','))}" width="{@width}" height="{@Height}" class="block" />
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates select="GateLayers" />
  </xsl:template>

  <xsl:template match="GateLayers">
    <xsl:apply-templates select="GateLayer" />
  </xsl:template>

  <xsl:template match="GateLayer">
    <xsl:choose>
      <xsl:when test="@positions">
        <xsl:variable name="path-data">
          <xsl:call-template name="convert-pairs-to-svg-path-data">
            <xsl:with-param name="value" select="@positions" />
            <xsl:with-param name="command" select="'M'" />
          </xsl:call-template>
        </xsl:variable>
        <svg:path d="{$path-data}" class="block" />
      </xsl:when>
      <xsl:when test="@position">
        <svg:rect x="{normalize-space(substring-before(@position, ','))}" y="{normalize-space(substring-after(@position, ','))}" width="{@width}" height="{@Height}" class="block" />
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates select="NetBlockLayers" />
  </xsl:template>

  <xsl:template match="NetBlockLayers">
    <xsl:apply-templates select="NetBlockLayer" />
  </xsl:template>

  <xsl:template match="NetBlockLayer">
    <xsl:choose>
      <xsl:when test="@positions">
        <xsl:variable name="path-data">
          <xsl:call-template name="convert-pairs-to-svg-path-data">
            <xsl:with-param name="value" select="@positions" />
            <xsl:with-param name="command" select="'M'" />
          </xsl:call-template>
        </xsl:variable>
        <svg:path d="{$path-data}" class="net-block" />
      </xsl:when>
      <xsl:when test="@position">
        <svg:rect x="{normalize-space(substring-before(@position, ','))}" y="{normalize-space(substring-after(@position, ','))}" width="{@width}" height="{@Height}" class="net-block" />
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates select="FloorLayers" />
  </xsl:template>

  <xsl:template match="FloorLayers">
    <xsl:apply-templates select="FloorLayer" />
  </xsl:template>

  <xsl:template match="FloorLayer">
    <xsl:choose>
      <xsl:when test="@positions">
        <xsl:variable name="path-data">
          <xsl:call-template name="convert-pairs-to-svg-path-data">
            <xsl:with-param name="value" select="@positions" />
            <xsl:with-param name="command" select="'M'" />
          </xsl:call-template>
        </xsl:variable>
        <svg:path d="{$path-data}" class="floor" />
      </xsl:when>
      <xsl:when test="@position">
        <xsl:variable name="x" select="normalize-space(substring-before(@position, ','))" />
        <xsl:variable name="y" select="normalize-space(substring-after(@position, ','))" />
        <xsl:variable name="width" select="@width" />
        <xsl:variable name="height" select="@Height" />
        <xsl:variable name="angle" select="@angle" />
        <svg:rect x="{$x}" y="{$y}" width="{$width}" height="{$height}" class="seat">
          <xsl:if test="@angle">
            <xsl:attribute name="transform">translate(<xsl:value-of select="$x" />,<xsl:value-of select="$y" />), rotate(<xsl:value-of select="$angle" />), translate(-<xsl:value-of select="$x" />,-<xsl:value-of select="$y" />), translate(-<xsl:value-of select="$width div 2" />, -<xsl:value-of select="$height div 2" />)</xsl:attribute>
          </xsl:if>
        </svg:rect>
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates select="RowLayers" />
  </xsl:template>

  <xsl:template match="RowLayers">
    <xsl:apply-templates select="RowLayer" />
  </xsl:template>

  <xsl:template match="RowLayer">
    <xsl:choose>
      <xsl:when test="@positions">
        <xsl:variable name="path-data">
          <xsl:call-template name="convert-pairs-to-svg-path-data">
            <xsl:with-param name="value" select="@positions" />
            <xsl:with-param name="command" select="'M'" />
          </xsl:call-template>
        </xsl:variable>
        <svg:path d="{$path-data}" class="row" />
      </xsl:when>
      <xsl:when test="@position">
        <xsl:variable name="x" select="normalize-space(substring-before(@position, ','))" />
        <xsl:variable name="y" select="normalize-space(substring-after(@position, ','))" />
        <xsl:variable name="width" select="@width" />
        <xsl:variable name="height" select="@Height" />
        <xsl:variable name="angle" select="@angle" />
        <svg:rect x="{$x}" y="{$y}" width="{$width}" height="{$height}" class="seat">
          <xsl:if test="@angle">
            <xsl:attribute name="transform">translate(<xsl:value-of select="$x" />,<xsl:value-of select="$y" />), rotate(<xsl:value-of select="$angle" />), translate(-<xsl:value-of select="$x" />,-<xsl:value-of select="$y" />), translate(-<xsl:value-of select="$width div 2" />, -<xsl:value-of select="$height div 2" />)</xsl:attribute>
          </xsl:if>
        </svg:rect>
      </xsl:when>
    </xsl:choose>
    <xsl:apply-templates select="SeatLayers" />
  </xsl:template>

  <xsl:template match="SeatLayers">
    <xsl:apply-templates select="SeatLayer" />
  </xsl:template>

  <xsl:template match="SeatLayer">
    <xsl:choose>
      <xsl:when test="@positions">
        <xsl:variable name="path-data">
          <xsl:call-template name="convert-pairs-to-svg-path-data">
            <xsl:with-param name="value" select="@positions" />
            <xsl:with-param name="command" select="'M'" />
          </xsl:call-template>
        </xsl:variable>
        <svg:path d="{$path-data}" class="seat" />
      </xsl:when>
      <xsl:when test="@position">
        <xsl:variable name="x" select="normalize-space(substring-before(@position, ','))" />
        <xsl:variable name="y" select="normalize-space(substring-after(@position, ','))" />
        <xsl:variable name="width" select="@width" />
        <xsl:variable name="height" select="@Height" />
        <xsl:variable name="angle" select="@angle" />
        <svg:rect x="{$x}" y="{$y}" width="{$width}" height="{$height}" class="seat">
          <xsl:if test="@angle">
            <xsl:attribute name="transform">translate(<xsl:value-of select="$x" />,<xsl:value-of select="$y" />), rotate(<xsl:value-of select="$angle" />), translate(-<xsl:value-of select="$x" />,-<xsl:value-of select="$y" />), translate(-<xsl:value-of select="$width div 2" />, -<xsl:value-of select="$height div 2" />)</xsl:attribute>
          </xsl:if>
        </svg:rect>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
<!--
vim: sts=2 sw=2 ts=2 et
-->
