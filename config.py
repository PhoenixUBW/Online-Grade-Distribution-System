class DefualtConfig():
    def __init__(self):
        self.__set_DEBUG(False)
        self.__set_SECRET_KEY("secret") #make safe
        self.__set_DB("users.db")
        self.__set_ADMIN_USERNAME("admin") #make safe
        self.__set_ADMIN_PASSPHRASE("admin") #make safe
        self.__set_EN_KEY(b'b79KmdHl5ijdRg3AMkvqfLYx_gvh9rLxiwoUS5QgZ54=') #make safe

    def __set_DEBUG(self,value):
        self.__DEBUG = value

    def __set_SECRET_KEY(self,value):
        self.__SECRET_KEY = value

    def __set_DB(self,value):
        self.__DB = value

    def __set_ADMIN_USERNAME(self,value):
        self.__ADMIN_USERNAME = value

    def __set_ADMIN_PASSPHRASE(self,value):
        self.__ADMIN_PASSPHRASE = value

    def __set_EN_KEY(self,value):
        self.__EN_KEY = value

    def get_SECRET_KEY(self):
        return self.__SECRET_KEY

    def get_DB(self):
        return self.__DB

    def get_ADMIN_USERNAME(self):
        return self.__ADMIN_USERNAME

    def get_ADMIN_PASSPHRASE(self):
        return self.__ADMIN_PASSPHRASE

    def get_EN_KEY(self):
        return self.__EN_KEY

class DevConfig(DefualtConfig):
    def __init__(self):
        self.set_DEBUG(True)

class ProductionConfig(DefualtConfig):
    def __init__(self):
        self.set_DEBUG(False)