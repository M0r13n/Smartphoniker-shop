def login(client, email: str, password: str):
    res = client.get("/admin/login/")
    form = res.forms[0]
    form["email"] = email
    form["password"] = password
    res = form.submit().follow()
    return res
