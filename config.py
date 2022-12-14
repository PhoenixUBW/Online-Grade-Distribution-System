class DefualtConfig():
    def __init__(self):
        self.set_DEBUG(False)
        self.set_SECRET_KEY("secret") #make safe
        self.set_USER_DB("users.db")
        self.set_GRADES_DB("grades.db")
        self.set_ADMIN_USERNAME("admin") #make safe
        self.set_ADMIN_PASSPHRASE("admin") #make safe
        self.set_EN_KEY(b'b79KmdHl5ijdRg3AMkvqfLYx_gvh9rLxiwoUS5QgZ54=') #make safe

    def set_DEBUG(self,value):
        self.__DEBUG = value

    def set_SECRET_KEY(self,value):
        self.__SECRET_KEY = value

    def set_USER_DB(self,value):
        self.__USER_DB = value
    
    def set_GRADES_DB(self,value):
        self.__GRADES_DB = value

    def set_ADMIN_USERNAME(self,value):
        self.__ADMIN_USERNAME = value

    def set_ADMIN_PASSPHRASE(self,value):
        self.__ADMIN_PASSPHRASE = value

    def set_EN_KEY(self,value):
        self.__EN_KEY = value
    
    def get_DEBUG(self):
        return self.__DEBUG

    def get_SECRET_KEY(self):
        return self.__SECRET_KEY

    def get_USER_DB(self):
        return self.__USER_DB
    
    def get_GRADES_DB(self):
        return self.__GRADES_DB

    def get_ADMIN_USERNAME(self):
        return self.__ADMIN_USERNAME

    def get_ADMIN_PASSPHRASE(self):
        return self.__ADMIN_PASSPHRASE

    def get_EN_KEY(self):
        return self.__EN_KEY

class DevConfig(DefualtConfig):
    def __init__(self):
        super().__init__()
        self.set_DEBUG(True)

class ProductionConfig(DefualtConfig):
    def __init__(self):
        super().__init__()
        self.set_DEBUG(False)