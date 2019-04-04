#!/usr/bin/env python3

from abc import ABC, abstractmethod

class Nonce:
    pass

class LogicalGate(ABC):
    arity = 0
    children = ()
    gate = 'Unknown'
    _nonce = None
    _memo = None

    def __init__(self, *children):
        assert len(children) == self.arity
        self.children = tuple(children)

    def value(self, nonce=None):
        # use memoization within a single call chain (same nonce)
        if nonce is None:
            nonce = Nonce()
        if nonce is not self._nonce:
            self._nonce = nonce
            inputs = [i.value(nonce) for i in self.children]
            self._memo = self._calc(*inputs)
        return self._memo

    def __repr__(self):
        nonce = Nonce()
        inpstr = ', '.join(str(i.value(nonce)) for i in self.children)
        if self.arity >= 2:
            inpstr = 'inputs: ' + inpstr + ', '
        elif self.arity == 1:
            inpstr = 'input: ' + inpstr + ', '
        return '<{} gate, {}value: {}>'.format(self.gate, inpstr, str(self.value(nonce)))

    @abstractmethod
    def _calc(self):
        pass


class InputGate(LogicalGate):
    gate = 'Input'
    arity = 0
    state = False

    def __init__(self, state=False):
        self.state = state

    def _calc(self):
        return self.state


class NotGate(LogicalGate):
    gate = 'NOT'
    arity = 1
    def _calc(self, a):
        return not a


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
    gate = 'IMPLY'
    arity = 2
    def _calc(self, a, b):
        return not a or b


class MultiGate(LogicalGate):
    def __init__(self, *children):
        self.arity = len(children)
        self.children = tuple(children)


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


def variables(n):
    return tuple(InputGate() for _ in range(n))


if __name__ == '__main__':
    a, b, c = variables(3)
    d, e, f = AndGate(a, b), AndGate(a, c), AndGate(b, c)
    g = MultiOrGate(d, e, f)
    bc = BooleanCircuit((a, b, c), g)
    assert bc(True, False, False) is False
    assert bc(True, True, False) is True

