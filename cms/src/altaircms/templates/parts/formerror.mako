%if form.errors:
    <ul class="alert nav">
        %for error in form.errors:
            <li>${error}: ${form.errors[error][0]}</li>
        %endfor
    </ul>
%endif
