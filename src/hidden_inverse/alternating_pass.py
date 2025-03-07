from pytket.passes import CustomPass
from pytket import Circuit, OpType


cx_replacement_circuit = Circuit(2)
cx_replacement_circuit.add_gate(OpType.PhasedX, [0.5, -0.5], [1])
cx_replacement_circuit.add_gate(OpType.ZZPhase, [1 / 2], [0, 1])
cx_replacement_circuit.add_gate(OpType.PhasedX, [-0.5, 0], [1])
cx_replacement_circuit.add_gate(OpType.Rz, [3 / 2], [1])
cx_replacement_circuit.add_gate(OpType.Rz, [7 / 2], [0])

cx_replacement_circuit_dg = cx_replacement_circuit.dagger()


def alternating_cnot_decomp(circ: Circuit) -> Circuit:
    """
    Transform function: Used to define the alternating CNOT decomposition pass.
    Given a Circuit containing the circuit is traversed and CNOTs are decomposed with
    two decompostions. If a CNOT has the same qubit indices as a previous CNOT then the
    hidden inverse decomposition is used.
    """
    ct_edges = [(i, i + 1) for i in range(circ.n_qubits - 1)]
    tc_edges = [(i + 1, i) for i in range(circ.n_qubits - 1)]
    total_edges = ct_edges + tc_edges
    bools = [True, False] * len(
        ct_edges
    )  # TODO have a (seeded) random sequence of booleans?
    edge_dict = {total_edges[i]: bools[i] for i in range(len(total_edges))}

    circ_prime = Circuit(circ.n_qubits)

    for cmd in circ.get_commands():
        if cmd.op.type == OpType.CX:
            edge = tuple([cmd.qubits[0].index[0], cmd.qubits[1].index[0]])
            if edge_dict[edge]:
                circ_prime.add_circuit(cx_replacement_circuit, cmd.qubits)
                edge_dict[edge] = not edge_dict[edge]
            else:
                circ_prime.add_circuit(cx_replacement_circuit_dg, cmd.qubits)
                edge_dict[edge] = not edge_dict[edge]
        else:
            circ_prime.add_gate(cmd.op.type, cmd.op.params, cmd.qubits)

    return circ_prime


alternating_cnots_pass = CustomPass(alternating_cnot_decomp)
