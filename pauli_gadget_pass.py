"""Script to apply the Hidden inverse technique to Pauli gadget circuits."""
from pytket import Circuit, OpType
from pytket.predicates import GateSetPredicate
from pytket.passes import CustomPass, DecomposeBoxes
from pytket.pauli import Pauli
from pytket.circuit import PauliExpBox
from pytket.circuit.display import view_browser
from pytket.utils import compare_unitaries

from hseires_decompositions import h_series_seq_pass, h_series_gateset_predicate
from phase_gadget_pass import get_phase_gadget, phase_gadget_hi_pass


single_qubit_cliffords = {OpType.H, OpType.V, OpType.Vdg}
pauli_gadget_predicate = GateSetPredicate(
    {OpType.Rz, OpType.CX} | single_qubit_cliffords
)


def _pauli_string_cutter(string: str) -> list[str]:
    """Helper function: Given a string splits the string into a list where each of
    the letters are an element of the list. 'XYZ' -> ['X', 'Y', 'Z']"""
    string2 = string.upper()
    mylist = []
    for letter in string2:
        assert letter in {"X", "Y", "Z", "I"}
        mylist.append(letter)
    return mylist


def _create_pauli(letter: str) -> Pauli:
    """
    Helper function: Given a Pauli letter A returns a Pauli.A object.
    """
    assert len(letter) == 1
    assert letter in {"X", "Y", "Z", "I"}
    pauli_dict = {"X": Pauli.X, "Y": Pauli.Y, "Z": Pauli.Z, "I": Pauli.I}
    return pauli_dict[letter]


def get_pauli_gadget(pauli_word: str, angle: float):
    """
    Returns a Pauli gadget circuit given a pauli word and an angle.
    """
    n_qubits = len(pauli_word)
    pauli_gadget_circ = Circuit(n_qubits)

    list_of_letters = _pauli_string_cutter(pauli_word)
    pauli_list = [_create_pauli(letter) for letter in list_of_letters]

    pauli_exp_box = PauliExpBox(pauli_list, angle)
    pauli_gadget_circ.add_pauliexpbox(pauli_exp_box, list(range(n_qubits)))
    DecomposeBoxes().apply(pauli_gadget_circ)
    return pauli_gadget_circ


def _partition_pauli_gadget(circ: Circuit) -> list[Circuit]:
    """
    Given a Pauli gadget circuit this function partitions the circuit before and
    after the central Rz gates returning a list of three circuits. The second circuit
    should just be a single Rz gate.
    """
    circuit_list = []
    n_qubits = circ.n_qubits

    assert (
        circ.n_gates_of_type(OpType.CX) + circ.n_gates_of_type(OpType.Rz)
        == 2 * n_qubits - 1
    )
    assert pauli_gadget_predicate.verify(circ)

    circ1 = Circuit(n_qubits)
    # TODO clean up this handling of Rz, its ugly
    for cmd in circ.get_commands():
        if cmd.op.type == OpType.Rz:
            pass
        else:
            circ1.add_gate(cmd.op.type, cmd.op.params, cmd.qubits)
        if cmd.op.type == OpType.Rz:
            circuit_list.append(circ1)
            circ2 = Circuit(1).add_gate(OpType.Rz, cmd.op.params, cmd.qubits)
            circuit_list.append(circ2)
            break

    circ3 = circ1.dagger()
    circuit_list.append(circ3)

    assert len(circuit_list) == 3
    return circuit_list


def transform_pauli_gadget(circ: Circuit) -> Circuit:
    """
    Transform function used to define the pauli_gadget_hi_pass Custom Pass.
    Given a Pauli gadget circuit returns a compiled circuit with the standard CNOT
    decomposition used before the Rz gate and the hidden inverse decomposition
    for CNOT^ after the Rz gate.
    """
    circ_prime = Circuit(circ.n_qubits)
    circuit_list = _partition_pauli_gadget(circ)
    h_series_seq_pass.apply(circuit_list[0])
    hidden_inverse_circ = circuit_list[0].dagger()

    circ_prime.append(circuit_list[0])
    circ_prime.add_circuit(circuit_list[1], [circ_prime.qubits[0]])
    circ_prime.append(hidden_inverse_circ)
    assert h_series_gateset_predicate.verify(circ_prime)
    return circ_prime


pauli_gadget_hi_pass = CustomPass(transform_pauli_gadget)


def test_pauli_gen() -> None:
    # test_pauli_circ = get_pauli_gadget("XYZX", 0.5)
    # view_browser(test_pauli_circ)
    # circuit_list = partition_pauli_gadget(test_pauli_circ)
    # for circ in circuit_list:
    #    view_browser(circ)
    pauli_circ = get_pauli_gadget("ZZ", 0.9)
    view_browser(pauli_circ)
    u1 = pauli_circ.get_unitary()
    pauli_gadget_hi_pass.apply(pauli_circ)
    u2 = pauli_circ.get_unitary()
    # view_browser(pauli_circ)
    print(compare_unitaries(u1, u2))


def compare_phase_and_pauli() -> None:
    circ1 = get_phase_gadget(0.9, 2)
    circ2 = get_pauli_gadget("ZZ", 0.9)
    phase_gadget_hi_pass.apply(circ1)
    pauli_gadget_hi_pass.apply(circ2)
    view_browser(circ1)
    view_browser(circ2)
    print(compare_unitaries(circ1.get_unitary(), circ2.get_unitary()))
    assert compare_unitaries(circ1.get_unitary(), circ2.get_unitary())


compare_phase_and_pauli()
# test_pauli_gen()