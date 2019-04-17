#!/usr/bin/env python3

from abc import ABC, abstractmethod

class Nonce:
    pass

class LogicalGate(ABC):
    arity = 0
    inputs = ()
    gate = 'Unknown'
    _nonce = None
    _memo = None

    def __init__(self, *inputs):
        assert len(inputs) == self.arity
        self.inputs = tuple(inputs)

    def value(self, nonce=None):
        # use memoization within a single call chain (same nonce)
        if nonce is None:
            nonce = Nonce()
        if nonce is not self._nonce:
            self._nonce = nonce
            inputs = [i.value(nonce) for i in self.inputs]
            self._memo = self._calc(*inputs)
        return self._memo

    def __repr__(self):
        #nonce = Nonce()
        #inpstr = ', '.join(str(i.value(nonce)) for i in self.inputs)
        #if self.arity >= 2:
        #    inpstr = 'inputs: ' + inpstr + ', '
        #elif self.arity == 1:
        #    inpstr = 'input: ' + inpstr + ', '
        #return '<{} gate, {}value: {}>'.format(self.gate, inpstr, str(self.value(nonce)))
        return '<{} gate, value: {}>'.format(self.gate, str(self.value()))

    def __bool__(self):
        return self.value()


    @abstractmethod
    def _calc(self):
        pass

    # we assign at least one operator to each nontrivial boolean function on <=2 inputs
    # (trying to be intuitive, but it's not always possible)
    def __invert__(self):          return NotGate(self)                #     ~a  NOT
    def __neg__(self):             return NotGate(self)                #     -a  NOT
    def __pos__(self):             return IdentGate(self)              #     +a  ID
    def __and__(self, other):      return AndGate(self, other)         #  a & b  AND
    def __mul__(self, other):      return AndGate(self, other)         #  a * b  AND
    def __or__(self, other):       return OrGate(self, other)          #  a | b  OR
    def __truediv__(self, other):  return OrGate(self, other)          #  a / b  OR
    def __xor__(self, other):      return XorGate(self, other)         #  a ^ b  XOR
    def __add__(self, other):      return XorGate(self, other)         #  a + b  XOR
    def __ne__(self, other):       return XorGate(self, other)         # a != b  XOR
    def __sub__(self, other):      return XnorGate(self, other)        #  a - b  XNOR
    def __eq__(self, other):       return XnorGate(self, other)        # a == b  XNOR
    def __matmul__(self, other):   return NandGate(self, other)        #  a @ b  NAND
    def __mod__(self, other):      return NorGate(self, other)         #  a % b  NOR
    def __lt__(self, other):       return CustomGate(2, self, other)   #  a < b  NRIMP
    def __rshift__(self, other):   return CustomGate(3, self, other)   # a >> b  RGT
    def __gt__(self, other):       return CustomGate(4, self, other)   #  a > b  NIMP
    def __lshift__(self, other):   return CustomGate(5, self, other)   # a << b  LFT
    def __pow__(self, other):      return CustomGate(10, self, other)  # a ** b  NLFT
    def __le__(self, other):       return CustomGate(11, self, other)  # a <= b  IMP
    def __floordiv__(self, other): return CustomGate(12, self, other)  # a // b  NRGT
    def __ge__(self, other):       return CustomGate(13, self, other)  # a >= b  RIMP


class InputGate(LogicalGate):
    gate = 'Input'
    arity = 0
    state = False

    def __init__(self, state=False):
        self.state = state

    def _calc(self):
        return self.state

    def set(self, state):
        self.state = state


class TrueGate(LogicalGate):
    gate = 'TRUE'
    arity = 0
    def _calc(self):
        return True


class FalseGate(LogicalGate):
    gate = 'FALSE'
    arity = 0
    def _calc(self):
        return False


class NotGate(LogicalGate):
    gate = 'NOT'
    arity = 1
    def _calc(self, a):
        return not a


class IdentGate(LogicalGate):
    gate = 'ID'
    arity = 1
    def _calc(self, a):
        return a


class AndGate(LogicalGate):
    gate = 'AND'
    arity = 2
    def _calc(self, a, b):
        return a and b


class OrGate(LogicalGate):
    gate = 'OR'
    arity = 2
    def _calc(self, a, b):
        return a or b


class NandGate(LogicalGate):
    gate = 'NAND'
    arity = 2
    def _calc(self, a, b):
        return not (a and b)


class NorGate(LogicalGate):
    gate = 'NOR'
    arity = 2
    def _calc(self, a, b):
        return not (a or b)


class XorGate(LogicalGate):
    gate = 'XOR'
    arity = 2
    def _calc(self, a, b):
        return a ^ b


class XnorGate(LogicalGate):
    gate = 'XNOR'
    arity = 2
    def _calc(self, a, b):
        return not (a ^ b)


class ImplyGate(LogicalGate):
    gate = 'IMP'
    arity = 2
    def _calc(self, a, b):
        return not a or b

class CustomGate(LogicalGate):
    arity = 2
    mode = 0

    def __init__(self, mode, *inputs):
        assert 0 <= mode < 16
        self.mode = mode
        self.gate = ['BOT', 'AND', 'NRIMP', 'RGT', 'NIMP', 'LFT', 'XOR', 'OR', 'NOR', 'XNOR', 'NLFT', 'IMP', 'NRGT', 'RIMP', 'NAND', 'TOP'][mode]
        super().__init__(*inputs)

    def _calc(self, a, b):
        return bool((self.mode << (a+2*b)) & 8)

class MultiGate(LogicalGate):
    def __init__(self, *inputs):
        self.arity = len(inputs)
        self.inputs = tuple(inputs)


class MultiAndGate(MultiGate):
    gate = 'AND'
    def _calc(self, *l):
        return all(l)


class MultiOrGate(MultiGate):
    gate = 'OR'
    def _calc(self, *l):
        return any(l)


class BooleanCircuit:
    inputs = None
    outputs = None

    def __init__(self, inputs, outputs):
        self.inputs = tuple(inputs)
        assert all(isinstance(i, InputGate) for i in self.inputs)
        if isinstance(outputs, LogicalGate):
            self.outputs = outputs
        else:
            self.outputs = tuple(outputs)
            assert all(isinstance(o, LogicalGate) for o in self.outputs)

    def __call__(self, *values):
        assert len(values) == len(self.inputs)
        for i, v in zip(self.inputs, values):
            i.state = v
        nonce = Nonce()
        if isinstance(self.outputs, LogicalGate):
            return self.outputs.value(nonce)
        else:
            return tuple(o.value(nonce) for o in self.outputs)


def InputGates(n):
    return tuple(InputGate() for _ in range(n))


if __name__ == '__main__':
    a, b, c = variables(3)
    d, e, f = AndGate(a, b), AndGate(a, c), AndGate(b, c)
    g = MultiOrGate(d, e, f)
    bc = BooleanCircuit((a, b, c), g)
    assert bc(True, False, False) is False
    assert bc(True, True, False) is True

