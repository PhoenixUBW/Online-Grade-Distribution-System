class DefualtConfig(object):
    def __init__(self):
        self.DEBUG = False
        self.SECRET_KEY = "secret"
        self.DB = "users.db"
        self.ADMIN_PASSPHRASE = "admin"
        self.EN_KEY = b'b79KmdHl5ijdRg3AMkvqfLYx_gvh9rLxiwoUS5QgZ54='

class DevConfig(DefualtConfig):
    def __init__(self):
        super().__init__()
        self.DEBUG = True

class ProductionConfig(DefualtConfig):
    def __init__(self):
        super().__init__()
        self.DEBUG = False