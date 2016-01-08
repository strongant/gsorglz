# _*_ coding: UTF-8 _*_
class User():
    """
    该类主要负责对用户的信息进行检测
    """
    def __init__(self,userName,password):
        self._userName = userName
        self._password = password




    def isValid(self,userName,password):
        result = True
        """
        用户有效性验证
        """
        return result



