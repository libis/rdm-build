# -*- coding: utf-8 -*-
"""
Created on Tue May 11 11:46:05 2021

@author: PieterDV
"""
# define Python user-defined exceptions
class myError(Exception):
    """Base class for other exceptions"""
    pass

class fileTransferError(myError):
    pass

class apiError(myError):
    pass

class orcidError(myError):
    pass

class liriasApiError(myError):
    pass

class liriasError(myError):
    pass

class moveFileError(myError):
    pass

#class ValueTooSmallError(Error):
 #   """Raised when the input value is too small"""
  #  pass


#class ValueTooLargeError(Error):
 #   """Raised when the input value is too large"""
  #  pass