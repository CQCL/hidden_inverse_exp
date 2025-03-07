import os
from glob import glob


from hidden_inverse.utils.circuit_builders import get_phase_gadget, get_pauli_gadget
from hidden_inverse.gadget_pass import (
    single_pauli_gadget_hi_pass,
)

from pytket import Circuit
from hidden_inverse.alternating_pass import alternating_cnots_pass


from pytket.utils import compare_unitaries
from pytket.qasm import circuit_from_qasm

PROJECT_FOLDER = os.path.dirname(os.path.abspath(__file__))
CIRCUITS_FOLDER = f"{PROJECT_FOLDER}/qasm_circuits"
circuit_files = glob(f"{CIRCUITS_FOLDER}/*.qasm")


def compare_phase_and_pauli_unitaries() -> None:
    circ_phase = get_phase_gadget(0.9, 2)
    circ_pauli = get_pauli_gadget("ZZ", 0.9)
    u1_phase = circ_phase.get_unitary()
    u1_pauli = circ_pauli.get_unitary()

    single_pauli_gadget_hi_pass.apply(circ_pauli)
    assert compare_unitaries(circ_phase.get_unitary(), circ_pauli.get_unitary())
    assert compare_unitaries(circ_phase.get_unitary(), u1_phase)
    assert compare_unitaries(circ_pauli.get_unitary(), u1_pauli)


def test_specific_pauli_gadget_circuits() -> None:
    pauli_yz = get_pauli_gadget("YZ", 0.7)
    pauli_xyyz = get_pauli_gadget("XYYZ", 0.65)

    u1_yz = pauli_yz.get_unitary()
    single_pauli_gadget_hi_pass.apply(pauli_yz)
    u2_yz = pauli_yz.get_unitary()
    assert compare_unitaries(u1_yz, u2_yz)

    u1_xyyz = pauli_xyyz.get_unitary()
    single_pauli_gadget_hi_pass.apply(pauli_xyyz)
    u2_xyyz = pauli_xyyz.get_unitary()
    assert compare_unitaries(u1_xyyz, u2_xyyz)


def test_depth1_pauli_gadget_qasm_circuits() -> None:
    counter = 1
    for circuit_file in circuit_files:
        print(f"Testing circuit: ({counter}/{len(circuit_files)})", circuit_file)
        pauli_circuit = circuit_from_qasm(circuit_file)
        u1 = pauli_circuit.get_unitary()
        single_pauli_gadget_hi_pass.apply(pauli_circuit)
        u2 = pauli_circuit.get_unitary()
        assert compare_unitaries(u1, u2)
        counter += 1


def test_alternating_cnot_decomposition():
    circuit = (
        Circuit(4)
        .H(0)
        .CX(0, 1)
        .H(1)
        .CX(1, 2)
        .H(3)
        .CX(2, 3)
        .H(3)
        .CX(0, 1)
        .H(1)
        .CX(1, 2)
        .CX(0, 1)
        .H(0)
        .H(1)
    )
    u1 = circuit.get_unitary()
    alternating_cnots_pass.apply(circuit)

    u2 = circuit.get_unitary()

    assert compare_unitaries(u1, u2)
