# _*_ coding: UTF-8 _*_
def enum(**enums):
    return type('Enum', (), enums)


# 具体含义请参见webservice中的state说明文档
# 1
# 成功
# -1
# 账号/密码错误
# -2
# 指定TaskId不存在
# -3
# 指定ResultId不存在
# -4
# 指定PackId不存在
# -5
# 指定任务已完成无法取消
# -6
# 数据校验失败
# -7
# 指定巡查任务未完成
# -8
# 非法参数
# -9
# 系统内部错误
# -10
# 文件已经存在
Codes = enum(SUCCESS="1", USERERROR="-1",
             TASKIDERROR="-2", RESULTIDERROR="-3",
             PACKIDERROR="-4", TASKNOCANCEL="-5",
             VALIDERROR="-6", TASKNOCOMPLETE="-7",
             PARAMSERROR='-8', INNERERROR="-9",
             COMPANYFILEISEXISTS="-10"
             )
