from ..lookup_tools.jersf_lookup import jersf_lookup
import warnings
import re
import numpy as np
from copy import deepcopy
from awkward import JaggedArray

def _checkConsistency(against,tocheck):
    if against is None:
        against = tocheck
    else:
        if against != tocheck:
            raise Exception('Corrector for {} is mixed'/
                            'with correctors for {}!'.format(tocheck,against))
    return tocheck

_levelre = re.compile('[L1-7]+')
def _getLevel(levelName):
    matches = _levelre.findall(levelName)
    if len(matches) > 1:
        raise Exception('Malformed JERSF level name: {}'.format(levelName))
    return matches[0]

_level_order = ['L1','L2','L3','L2L3']

class JetResolutionScaleFactor(object):
    def __init__(self,**kwargs):
        jettype = None
        levels = []
        funcs = []
        datatype = None
        campaign = None
        dataera = None
        for name,func in kwargs.items():
            if not isinstance(func,jersf_lookup):
                raise Exception('{} is a {} and not a jersf_lookup!'.format(name,type(func)))
            info = name.split('_')
            if len(info) != 5:
                raise Exception('Corrector name is not properly formatted!')
            
            campaign = _checkConsistency(campaign,info[0])
            dataera  = _checkConsistency(dataera,info[1])
            datatype = _checkConsistency(datatype,info[2])
            levels.append(info[3])
            funcs.append(func)
            jettype  = _checkConsistency(jettype,info[4])
        
        if campaign is None:
            raise Exception('Unable to determine production campaign of JECs!')
        else:
            self._campaign = campaign
        
        if dataera is None:
            raise Exception('Unable to determine data era of JECs!')
        else:
            self._dataera = dataera
        
        if datatype is None:
            raise Exception('Unable to determine if JECs are for MC or Data!')
        else:
            self._datatype = datatype
        
        if len(levels) == 0:
            raise Exception('No levels provided?')
        else:
            self._levels = levels
            self._funcs = funcs
        
        if jettype is None:
            raise Exception('Unable to determine type of jet to correct!')
        else:
            self._jettype = jettype
        
        for i,level in enumerate(self._levels):
            this_level = _getLevel(level)
            ord_idx = _level_order.index(this_level)
            if i != this_level:
                self._levels[i],self._levels[ord_idx] = self._levels[ord_idx],self._levels[i]
                self._funcs[i],self._funcs[ord_idx] = self._funcs[ord_idx],self._funcs[i]
    
        #now we setup the call signature for this factorized JEC
        self._signature = []
        for func in self._funcs:
            sig = func.signature
            for input in sig:
                if input not in self._signature:
                    self._signature.append(input)

    @property
    def signature(self):
        return self._signature
    
    def __repr__(self):
        out  = 'campaign   : %s\n'%(self._campaign)
        out += 'data era   : %s\n'%(self._dataera)
        out += 'data type  : %s\n'%(self._datatype)
        out += 'jet type   : %s\n'%(self._jettype)
        out += 'levels     : %s\n'%(','.join(self._levels))
        out += 'signature  : (%s)\n'%(','.join(self._signature))
        return out
    
    def getScaleFactor(self,**kwargs):
        sfs = []
        for i,func in enumerate(self._funcs):
            sig = func.signature
            args = []
            for input in sig:
                args.append(localargs[input])
            sfs.append(func(*tuple(args)))
        return tuple(sfs)
    
    
