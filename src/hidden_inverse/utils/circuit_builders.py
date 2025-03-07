from pytket.circuit import Circuit, PauliExpBox
from pytket.pauli import Pauli
from pytket.passes import DecomposeBoxes


def get_phase_gadget(rz_angle: float, n_qubits: int) -> Circuit:
    """
    Creates a phase gadget circuit for a given Rz angle and number of qubits.
    """

    assert n_qubits > 1
    circ = Circuit(n_qubits)

    for qubit in range(n_qubits - 1):
        circ.CX(qubit, qubit + 1)

    circ.Rz(rz_angle, n_qubits - 1)

    for qubit in reversed(range(n_qubits - 1)):
        circ.CX(qubit, qubit + 1)

    return circ


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


def get_pauli_gadget(pauli_word: str, angle: float, decompose=True) -> Circuit:
    """
    Returns a Pauli gadget circuit given a pauli word and an angle.
    Optional flag to decompose the PauliExpBox or not (default=True).
    """
    n_qubits = len(pauli_word)
    pauli_gadget_circ = Circuit(n_qubits)

    list_of_letters = _pauli_string_cutter(pauli_word)
    pauli_list = [_create_pauli(letter) for letter in list_of_letters]

    pauli_exp_box = PauliExpBox(pauli_list, angle)
    pauli_gadget_circ.add_pauliexpbox(pauli_exp_box, list(range(n_qubits)))
    if decompose:
        DecomposeBoxes().apply(pauli_gadget_circ)
    return pauli_gadget_circ
