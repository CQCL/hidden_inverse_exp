"""Script to generate H-Series decompositions for any two qubit unitary with a hidden inverse"""

import numpy as np
from pytket.circuit import OpType, Circuit, Unitary1qBox, Unitary2qBox
from pytket.predicates import GateSetPredicate
from pytket.passes import (
    SequencePass,
    DecomposeBoxes,
    FullPeepholeOptimise,
    NormaliseTK2,
    DecomposeTK2,
    AutoRebase,
    RemoveRedundancies,
    AutoSquash,
)
from pytket.utils import compare_unitaries


hseries_rebase = AutoRebase({OpType.ZZPhase, OpType.Rz, OpType.PhasedX})
hseries_squash = AutoSquash({OpType.PhasedX, OpType.Rz})

h_series_seq_pass = SequencePass(
    [
        DecomposeBoxes(),
        FullPeepholeOptimise(target_2qb_gate=OpType.TK2),
        NormaliseTK2(),
        DecomposeTK2(),
        hseries_rebase,
        RemoveRedundancies(),
        hseries_squash,
    ]
)
h_series_gateset_predicate = GateSetPredicate(
    {OpType.ZZPhase, OpType.ZZMax, OpType.Rz, OpType.PhasedX}
)

h_series_gateset_predicate_1q = GateSetPredicate({OpType.Rz, OpType.PhasedX})


# These functions are basically duplicates and should maybe be combined into one.
def get_hidden_inverse_circuits_1q(unitary_1q: np.array) -> tuple[Circuit, Circuit]:
    """
    Given a 1 qubit unitary A that is self-adjoint returns the decomposition of A as well as the
    decomposition of A^. Both decompositions are in the H-series gateset.
    """
    assert unitary_1q.shape == (2, 2)
    assert np.allclose(
        unitary_1q, unitary_1q.conj().T
    )  # assert that 1q unitary is self-adjoint
    u_box_1q = Unitary1qBox(unitary_1q)
    circ_1q = Circuit(1)
    circ_1q.add_unitary1qbox(u_box_1q, 0)
    h_series_seq_pass.apply(circ_1q)
    assert h_series_gateset_predicate_1q.verify(circ_1q)
    assert compare_unitaries(circ_1q.get_unitary(), unitary_1q)
    assert compare_unitaries(circ_1q.dagger().get_unitary(), unitary_1q)
    return (circ_1q, circ_1q.dagger())


# The function below should generate pairs of Hidden inverses for any two qubit unitary
#  that is self-adjoint. The decompositions are given in the H-Series gateset.
def get_hidden_inverse_circuits_2q(unitary_2q: np.array) -> tuple[Circuit, Circuit]:
    """
    Given a 2 qubit unitary A that is self-adjoint returns the decomposition of A as well as the
    decomposition of A^. Both decompositions are in the H-series gateset.
    """
    assert unitary_2q.shape == (4, 4)
    assert np.allclose(
        unitary_2q, unitary_2q.conj().T
    )  # assert that 2q unitary is self-adjoint
    u_box_2q = Unitary2qBox(unitary_2q)
    circ_2q = Circuit(2)
    circ_2q.add_unitary2qbox(u_box_2q, 0, 1)
    h_series_seq_pass.apply(circ_2q)
    assert h_series_gateset_predicate.verify(circ_2q)
    assert compare_unitaries(circ_2q.get_unitary(), unitary_2q)
    assert compare_unitaries(circ_2q.dagger().get_unitary(), unitary_2q)
    return (circ_2q, circ_2q.dagger())
