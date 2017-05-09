def load_users(filename):
    with open(filename) as f:
        data = f.readlines()[1:]
        users = {}
        for row in data:
            [username, password, secret_key] = row.strip().split(",")
            users[username] = {
                'password': password,
                'secret_key': secret_key
            }
    return users
