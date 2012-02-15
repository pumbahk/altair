<%def name="form()">
    var stylesheets = ['/static/deform/css/beautify.css'];

    function deform_ajaxify(response, status, xhr, form, oid, mthd){
        var options = {
            target: '#' + oid,
            replaceTarget: true,
            success: function(response, status, xhr, form){
                deform_ajaxify(response, status, xhr, form, oid);
            }
        };
        var extra_options = {};
        var name;
        if (extra_options) {
            for (name in extra_options) {
                options[name] = extra_options[name];
            };
        };
        $('#' + oid).ajaxForm(options);
        if(mthd){
            mthd(response, status, xhr, form);
        }
    }
    deform.addCallback(
            'deform',
            function(oid) {
                deform_ajaxify(null, null, null, null, oid);
            }
    );
    deform.load();
</%def>
