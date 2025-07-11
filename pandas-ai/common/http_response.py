
class HttpResponse:
  """标准HTTP响应封装类
  
  属性:
      code: 状态码(默认200)
      msg: 响应消息(默认'成功')
      data: 响应数据(默认None)
  """
  def __init__(self, code=200, msg='成功', data=None):
    self.code = code
    self.msg = msg
    self.data = data

  def to_dict(self):
    """转换为字典格式"""
    return {
      'code': self.code,
      'msg': self.message,
      'data': self.data
    }

  @classmethod
  def success(cls, data=None):
    """快速创建成功响应"""
    return cls(200, '操作成功', data)

  @classmethod
  def error(cls, code=500, msg='服务器错误'):
    """快速创建错误响应"""
    return cls(code, msg, None)
