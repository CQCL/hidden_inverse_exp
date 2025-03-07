import numpy as np
from pytket import Circuit

from pytket.qasm import circuit_to_qasm
from pytket.circuit import PauliExpBox
from pytket.pauli import Pauli


pauli_list = [Pauli.X, Pauli.Y, Pauli.Z, Pauli.I]


def generate_random_gadget(n_qubits: int, depth: int, save_qasm=False) -> Circuit:

    c = Circuit(n_qubits)

    qubit_list = [i for i in range(n_qubits)]

    for _ in range(depth):
        # Randomly reorder the qubits on which the gate will act, generate
        # random angle, and choose random Pauli string.
        # subset = np.random.permutation(qubit_list)
        subset = np.random.RandomState(seed=42).permutation(qubit_list)
        # angle = np.random.uniform(-2, 2)
        angle = 0.65
        random_pauli = np.random.choice(pauli_list, n_qubits)

        # Generate gate corresponding to pauli string and angle
        pauli_box = PauliExpBox(random_pauli, angle)
        c.add_pauliexpbox(pauli_box, subset)

        if save_qasm:
            circuit_to_qasm(c, f"pauli_gadget_q{n_qubits}_d{depth}.qasm")

    return c
