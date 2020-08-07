from ldap.controls import SimplePagedResultsControl


# https://stackoverflow.com/a/61829690/2630074
def paginated_query(connect, attributes, base, scope, search_flt):
    # how many users to search for in each page,
    # this depends on the server maximum setting
    # (default highest value is 1000)
    page_size = 500

    req_ctrl = SimplePagedResultsControl(
        criticality=True, size=page_size, cookie=""
    )
    msgid = connect.search_ext(
        base=base,
        scope=scope,
        filterstr=search_flt,
        attrlist=attributes,
        serverctrls=[req_ctrl],
    )

    total_results = []
    pages = 0
    while True:  # loop over all of the pages using the same cookie,
        # otherwise the search will fail
        pages += 1
        rtype, rdata, rmsgid, serverctrls = connect.result3(msgid)
        for user in rdata:
            total_results.append(user)

        pctrls = [
            c
            for c in serverctrls
            if c.controlType == SimplePagedResultsControl.controlType
        ]
        if pctrls:
            if pctrls[
                0
            ].cookie:  # Copy cookie from response control to request control
                req_ctrl.cookie = pctrls[0].cookie
                msgid = connect.search_ext(
                    base=base,
                    scope=scope,
                    filterstr=search_flt,
                    attrlist=attributes,
                    serverctrls=[req_ctrl],
                )
            else:
                break
        else:
            break
    return total_results
