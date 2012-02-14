<%inherit file='altaircms:templates/front/simple/layout.mako'/>

<div class="section section-main">
    <div id="block_name">
        %if 'block_name' in display_blocks:
            %for widget in display_blocks['block_name']:
               ${widget|n}
            %endfor
        %endif
    </div>
</div>

