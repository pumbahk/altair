<html>
    <body>
    <form ${request.route_url('top')} method="post">
        <ul>
            <li>
                <label>card_number</label>
                <input name="card_number" />
            </li>
            <li>
                <label>card_holder_name</label>
                <input name="card_holder_name" />
            </li>
            <li>
                <label>mail_address</label>
                <input name="mail_address" />
            </li>
            <li>
                <label>exp_month</label>
                <input name="exp_month" />
            </li>
            <li>
                <label>exp_year</label>
                <input name="exp_year" />
            </li>
            <li>
                <label>total_amount</label> 10
                <input type="hidden" value="10" name="total_amount" />
            </li>
        </ul>
        <button type="submit">Submit</button>
    </form>
    </body>
</html>