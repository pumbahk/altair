<?xml version="1.0" encoding="UTF-8" ?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:svg="http://www.w3.org/2000/svg"
    xmlns:si="http://xmlns.ticketstar.jp/2012/site-info"
    xmlns:exslt="http://exslt.org/common"
    xmlns:msxsl="urn:schemas-microsoft-com:xslt"
    extension-element-prefixes="exslt msxsl"
    version="1.0">
  <xsl:param name="ignore-appearance-styles" select="true()" />
  <xsl:param name="render-blocks" select="true()" />
  <xsl:param name="render-row-numbers" select="true()" />
  <xsl:param name="scale" select="number(.1)" />

  <xsl:output method="xml" encoding="utf-8" indent="yes" />

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

  <!-- converts "r,g,b,a" representation of a color to the form "rgb(r, g, b) by simply ignoring the alpha value -->
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
    <xsl:variable name="first-chunk" select="normalize-space(substring-before($value, ','))" />
    <xsl:variable name="remainder" select="normalize-space(substring-after($value, ','))" />
      <xsl:value-of select="number($first-chunk) * $scale" /><xsl:text> </xsl:text><xsl:choose>
      <xsl:when test="contains($remainder, ',')">
        <xsl:value-of select="number(normalize-space(substring-before($remainder, ','))) * $scale" /><xsl:text> </xsl:text>
        <xsl:call-template name="convert-pairs-to-svg-path-data"><xsl:with-param name="value" select="normalize-space(substring-after($remainder, ','))" /></xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="number($remainder) * $scale" />
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="/Hall">
    <xsl:variable name="width" select="number(normalize-space(substring-before(InitialViewStatus/Center, ','))) * 4 * $scale" />
    <xsl:variable name="height" select="number(normalize-space(substring-after(InitialViewStatus/Center, ','))) * 6 * $scale" />
    <svg:svg version="1.1" viewBox="0 0 {$width} {$height}" preserveAspectRatio="xMinYMin meet" si:version="0.0">
      <svg:title><xsl:value-of select="Name" /></svg:title>
      <svg:metadata xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
                    xmlns:dc="http://purl.org/dc/elements/1.1/">
        <si:object>
          <si:class>Venue</si:class>
          <si:property name="name"><xsl:value-of select="Name" /></si:property>
        </si:object>
        <si:description>
          <si:gettii-id><xsl:value-of select="ID" /></si:gettii-id>
          <si:title><xsl:value-of select="Name" /></si:title>
        </si:description>
        <rdf:RDF>
          <rdf:Description>
            <dc:title><xsl:value-of select="Name" /></dc:title>
          </rdf:Description>
        </rdf:RDF>
      </svg:metadata>
      <svg:style type="text/css">
        <xsl:choose>
          <xsl:when test="$ignore-appearance-styles">
            <xsl:message>Appearance styles will be ignored.</xsl:message>
            <xsl:text>
.block {
  fill: rgb(255, 255, 192);
  stroke: rgb(0, 0, 0);
  stroke-width: 1px;
  vector-effect: non-scaling-stroke;
}

.seat {
  fill: rgb(160, 160, 160);
  stroke: rgb(0, 0, 0);
  stroke-width: 1px;
  vector-effect: non-scaling-stroke;
}
            </xsl:text>
          </xsl:when>
          <xsl:otherwise>
            <xsl:apply-templates select="BlockLayerAttribute|GateLayerAttribute|RowLayerAttribute|SeatLayerAttribute" mode="css" />
          </xsl:otherwise>
        </xsl:choose>
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
    <xsl:param name="indent" select="''" />
    <xsl:apply-templates select="BlockLayer">
      <xsl:with-param name="indent" select="$indent" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="BlockLayer">
    <xsl:param name="indent" />
    <xsl:message><xsl:value-of select="$indent" />Processing block layer <xsl:value-of select="@name" /></xsl:message>
    <svg:g id="{generate-id()}">
      <svg:title><xsl:value-of select="@name" /></svg:title>
      <svg:metadata>
        <si:object>
          <si:class>Block</si:class>
          <si:property name="name"><xsl:value-of select="@name" /></si:property>
        </si:object>
      </svg:metadata>
      <xsl:if test="$render-blocks">
        <xsl:choose>
          <xsl:when test="@positions">
            <xsl:variable name="path-data">
              <xsl:text>M </xsl:text>
              <xsl:call-template name="convert-pairs-to-svg-path-data">
                <xsl:with-param name="value" select="@positions" />
              </xsl:call-template>
              <xsl:text> Z</xsl:text>
            </xsl:variable>
            <svg:path d="{$path-data}" class="block" />
          </xsl:when>
          <xsl:when test="@position">
            <xsl:variable name="x" select="number(normalize-space(substring-before(@position, ','))) * $scale" />
            <xsl:variable name="y" select="number(normalize-space(substring-after(@position, ','))) * $scale" />
            <xsl:variable name="width" select="number(normalize-space(@width)) * $scale" />
            <xsl:variable name="height" select="number(normalize-space(@Height)) * $scale" />
            <xsl:variable name="angle" select="@angle" />
            <svg:rect x="{$x}" y="{$y}" width="{$width}" height="{$height}" id="{$id}" class="block">
              <xsl:if test="$angle">
                <xsl:attribute name="transform">
                  <xsl:text>rotate(</xsl:text>
                  <xsl:value-of select="$angle" />
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="$x" />
                  <xsl:text> </xsl:text>
                  <xsl:value-of select="$y" />
                  <xsl:text>)</xsl:text>
                </xsl:attribute>
              </xsl:if>
            </svg:rect>
          </xsl:when>
        </xsl:choose>
      </xsl:if>
      <xsl:apply-templates select="GateLayers">
        <xsl:with-param name="indent" select="concat($indent, '  ')" />
      </xsl:apply-templates>
    </svg:g>
  </xsl:template>

  <xsl:template match="GateLayers">
    <xsl:param name="indent" />
    <xsl:apply-templates select="GateLayer">
      <xsl:with-param name="indent" select="$indent" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="GateLayer">
    <xsl:param name="indent" />
    <xsl:message><xsl:value-of select="$indent" />Processing gate layer <xsl:value-of select="@name" /></xsl:message>
    <xsl:apply-templates select="NetBlockLayers">
      <xsl:with-param name="indent" select="concat($indent, '  ')" />
      <xsl:with-param name="gate" select="@name" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="NetBlockLayers">
    <xsl:param name="indent" />
    <xsl:param name="gate" />
    <xsl:apply-templates select="NetBlockLayer">
      <xsl:with-param name="indent" select="$indent" />
      <xsl:with-param name="gate" select="$gate" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="NetBlockLayer">
    <xsl:param name="indent" />
    <xsl:param name="gate" />
    <xsl:apply-templates select="FloorLayers">
      <xsl:with-param name="indent" select="$indent" />
      <xsl:with-param name="gate" select="$gate" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="FloorLayers">
    <xsl:param name="indent" />
    <xsl:param name="gate" />
    <xsl:apply-templates select="FloorLayer">
      <xsl:with-param name="indent" select="$indent" />
      <xsl:with-param name="gate" select="$gate" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="FloorLayer">
    <xsl:param name="indent" />
    <xsl:param name="gate" />
    <xsl:message><xsl:value-of select="$indent" />Processing floor layer <xsl:value-of select="@name" /></xsl:message>
    <xsl:apply-templates select="RowLayers">
      <xsl:with-param name="indent" select="concat($indent, '  ')" />
      <xsl:with-param name="gate" select="$gate" />
      <xsl:with-param name="floor" select="@name" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="RowLayers">
    <xsl:param name="indent" />
    <xsl:param name="gate" />
    <xsl:param name="floor" />
    <xsl:apply-templates select="RowLayer">
      <xsl:with-param name="indent" select="$indent" />
      <xsl:with-param name="gate" select="$gate" />
      <xsl:with-param name="floor" select="$floor" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="RowLayer">
    <xsl:param name="indent" />
    <xsl:param name="gate" />
    <xsl:param name="floor" />
    <xsl:message><xsl:value-of select="$indent" />Processing row layer <xsl:value-of select="@name" /></xsl:message>
    <svg:g id="{generate-id()}">
      <xsl:variable name="seat-prototype-id" select="generate-id()" />
      <svg:title><xsl:value-of select="@name" /></svg:title>
      <svg:metadata>
        <si:object>
          <si:class>Row</si:class>
          <si:property name="name"><xsl:value-of select="@name" /></si:property>
        </si:object>
        <si:prototype id="{$seat-prototype-id}">
          <si:class>Seat</si:class>
          <si:property name="gate"><xsl:value-of select="$gate" /></si:property>
          <si:property name="floor"><xsl:value-of select="$floor" /></si:property>
        </si:prototype>
      </svg:metadata>
      <xsl:apply-templates select="SeatLayers">
        <xsl:with-param name="indent" select="concat($indent, '  ')" />
        <xsl:with-param name="seat-prototype-id" select="$seat-prototype-id" />
      </xsl:apply-templates>
      <xsl:if test="$render-row-numbers">
        <xsl:variable name="x" select="number(normalize-space(substring-before(@position, ','))) * $scale" />
        <xsl:variable name="y" select="number(normalize-space(substring-after(@position, ','))) * $scale" />
        <xsl:variable name="width" select="number(normalize-space(@width)) * $scale" />
        <xsl:variable name="height" select="number(normalize-space(@Height)) * $scale" />
        <xsl:variable name="angle" select="@angle" />
        <svg:text x="{$x}" y="{$y + $height * .75}" width="{$width}" height="{$height}" class="row" style="font-size: {$height * .75}px" transform="ref(svg)">
          <xsl:if test="$angle">
            <xsl:attribute name="transform">
              <xsl:text>rotate(</xsl:text>
              <xsl:value-of select="$angle" />
              <xsl:text> </xsl:text>
              <xsl:value-of select="$x" />
              <xsl:text> </xsl:text>
              <xsl:value-of select="$y" />
              <xsl:text>)</xsl:text>
            </xsl:attribute>
          </xsl:if>
          <xsl:value-of select="@name" />
        </svg:text>
      </xsl:if>
    </svg:g>
  </xsl:template>

  <xsl:template match="SeatLayers">
    <xsl:param name="indent" />
    <xsl:param name="seat-prototype-id" />
    <xsl:apply-templates select="SeatLayer">
      <xsl:with-param name="indent" select="$indent" />
      <xsl:with-param name="seat-prototype-id" select="$seat-prototype-id" />
    </xsl:apply-templates>
  </xsl:template>

  <xsl:template match="SeatLayer">
    <xsl:param name="indent" />
    <xsl:param name="seat-prototype-id" />
    <xsl:message><xsl:value-of select="$indent" />Processing seat layer <xsl:value-of select="@name" /></xsl:message>
    <xsl:variable name="id" select="generate-id()" />
    <xsl:choose>
      <xsl:when test="@positions">
        <xsl:variable name="path-data">
          <xsl:call-template name="convert-pairs-to-svg-path-data">
            <xsl:with-param name="value" select="@positions" />
            <xsl:with-param name="command" select="'M'" />
          </xsl:call-template>
          <xsl:text> Z</xsl:text>
        </xsl:variable>
        <svg:path d="{$path-data}" id="{$id}" class="seat">
          <svg:title><xsl:value-of select="@name" /></svg:title>
          <svg:metadata>
            <si:object prototype="{$seat-prototype-id}">
              <si:class>Seat</si:class>
              <si:property name="name"><xsl:value-of select="@name" /></si:property>
            </si:object>
          </svg:metadata>
        </svg:path>
      </xsl:when>
      <xsl:when test="@position">
        <xsl:variable name="x" select="number(normalize-space(substring-before(@position, ','))) * $scale" />
        <xsl:variable name="y" select="number(normalize-space(substring-after(@position, ','))) * $scale" />
        <xsl:variable name="width" select="number(@width) * $scale" />
        <xsl:variable name="height" select="number(@Height) * $scale" />
        <xsl:variable name="angle" select="@angle" />
        <svg:rect x="{$x}" y="{$y}" width="{$width}" height="{$height}" id="{$id}" class="seat">
          <xsl:if test="$angle">
            <xsl:attribute name="transform">
              <xsl:text>rotate(</xsl:text>
              <xsl:value-of select="$angle" />
              <xsl:text> </xsl:text>
              <xsl:value-of select="$x" />
              <xsl:text> </xsl:text>
              <xsl:value-of select="$y" />
              <xsl:text>)</xsl:text>
            </xsl:attribute>
          </xsl:if>
          <svg:title><xsl:value-of select="@name" /></svg:title>
          <svg:metadata>
            <si:object prototype="{$seat-prototype-id}">
              <si:class>Seat</si:class>
              <si:property name="name"><xsl:value-of select="@name" /></si:property>
            </si:object>
          </svg:metadata>
        </svg:rect>
      </xsl:when>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
<!--
vim: sts=2 sw=2 ts=2 et
-->
