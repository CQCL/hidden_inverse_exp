"""Script to apply the Hidden inverse technique to Pauli gadget circuits."""

from pytket import Circuit, OpType
from pytket.predicates import GateSetPredicate
from pytket.passes import CustomPass, DecomposeBoxes
from pytket.circuit import PauliExpBox


from .hseries import h_series_seq_pass, h_series_gateset_predicate


single_qubit_cliffords = {OpType.H, OpType.V, OpType.Vdg}
pauli_gadget_predicate = GateSetPredicate(
    {OpType.Rz, OpType.CX} | single_qubit_cliffords
)
gadget_boxes = {OpType.PhasePolyBox, OpType.PauliExpBox}


def _partition_pauli_gadget(circ: Circuit) -> list[Circuit]:
    """
    Given a Pauli gadget circuit this function partitions the circuit before and
    after the central Rz gates returning a list of three circuits. The second circuit
    should just be a single Rz gate.
    """
    assert pauli_gadget_predicate.verify(circ)

    circuit_list = []
    n_qubits = circ.n_qubits

    lhs_circ = Circuit(n_qubits)
    for cmd in circ.get_commands():
        if cmd.op.type != OpType.Rz:
            lhs_circ.add_gate(cmd.op.type, cmd.op.params, cmd.qubits)
        elif cmd.op.type == OpType.Rz:
            circuit_list.append(lhs_circ)
            rz_index = cmd.qubits
            rz_circ = Circuit(n_qubits).add_gate(OpType.Rz, cmd.op.params, rz_index)
            circuit_list.append(rz_circ)
            break

    rhs_circ = lhs_circ.dagger()
    circuit_list.append(rhs_circ)

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
    circ_prime.add_circuit(
        circuit_list[1], [circ_prime.qubits[0]]
    )  # add central Rz gate to q[0]
    circ_prime.append(hidden_inverse_circ)
    assert h_series_gateset_predicate.verify(circ_prime)
    return circ_prime


single_pauli_gadget_hi_pass = CustomPass(transform_pauli_gadget)


def transform_pauli_exp_box_circuit(circ: Circuit) -> Circuit:
    """
    Transform function: Given a circuit containing PauliExpBox(es)
    and PhasePolyBox(es) returns a circuit with the Pauli gadgets
    implemented using the H-Series hidden inverse decompositions.
    """
    circ_prime = Circuit(circ.n_qubits, circ.n_bits, name=circ.name)
    for cmd in circ.get_commands():
        if cmd.op.type == OpType.Measure:
            circ_prime.Measure(cmd.args[0], cmd.args[1])
        elif cmd.op.type not in gadget_boxes:
            circ_prime.add_gate(cmd.op.type, cmd.op.params, cmd.qubits)
        else:
            box_circ = Circuit(len(cmd.qubits))
            pauli_list = cmd.op.get_paulis()
            angle = cmd.op.get_phase()
            p_exp_box = PauliExpBox(pauli_list, angle)
            box_circ.add_pauliexpbox(p_exp_box, box_circ.qubits)
            DecomposeBoxes().apply(box_circ)
            single_pauli_gadget_hi_pass.apply(box_circ)
            circ_prime.add_circuit(box_circ, cmd.qubits)

    return circ_prime


general_pauli_gadget_hi_pass = CustomPass(transform_pauli_exp_box_circuit)
