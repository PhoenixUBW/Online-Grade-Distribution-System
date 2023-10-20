# Default config settings
class DefualtConfig():
    def __init__(self):
        self.set_DEBUG(False) # Debug off by defauly
        self.set_SECRET_KEY("secret") # Session key
        self.set_USER_DB("users.db") # User database filename
        self.set_GRADES_DB("grades.db") # Student grade database filename
        self.set_ADMIN_USERNAME("admin") # Admin username
        self.set_ADMIN_PASSPHRASE("admin") # Admin passphrase
        self.set_EN_KEY(b'b79KmdHl5ijdRg3AMkvqfLYx_gvh9rLxiwoUS5QgZ54=') # Encryption key

    def set_DEBUG(self,value): # Uses set methods to set the private values
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
    
    def get_DEBUG(self): # Uses get methods to retrieve the private attributes
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

# Developer config settings
class DevConfig(DefualtConfig):
    def __init__(self):
        super().__init__() # Inherets all the default config settings
        self.set_DEBUG(True) # Overides debug to be true

# Production config settigngs
class ProductionConfig(DefualtConfig):
    def __init__(self):
        super().__init__() # Inherets all the default config settings
        self.set_DEBUG(False) # Overides debug to be false