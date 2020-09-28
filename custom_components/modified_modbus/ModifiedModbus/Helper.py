'''
Created on Sep 13, 2020

@author: pc
'''
from builtins import staticmethod

class Helper(object):
    '''
    byte operations
    '''
    @staticmethod
    def convertBytesToHoldings(byteHoldings):
        ints16 = []
        i = 0
        # Iterating using while loop 
        while i < len(byteHoldings)-1: 
            twobytes = bytes([byteHoldings[i],byteHoldings[i+1]])
            intv = int.from_bytes(twobytes, "big")
            ints16.append(intv)    
            i += 2
        return ints16
    
    @staticmethod
    def convertHoldingsToBytes(holdings):
        result = []
        for i in holdings:
            result.append(i.to_bytes(2, byteorder='big')[0])
            result.append(i.to_bytes(2, byteorder='big')[1])
        return bytes(result)
        

    @staticmethod
    def printHoldings(holdings):
        result = ""
        for i in holdings:
            result = result + "{0:04x} ".format(i)
        print(result)

    
    
        