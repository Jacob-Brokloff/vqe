from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit_ibm_runtime import EstimatorV2 as IBMEstimator
from scipy.optimize import minimize
from functools import partial
from dataclasses import dataclass, field
import numpy as np
import matplotlib.pyplot as plt

def _build_ansatz(n: int, d: int) -> QuantumCircuit:
    p = ParameterVector("θ", n * d * 2)
    qc = QuantumCircuit(n)
    idx = 0
    for _ in range(d):
        for q in range(n):
            qc.ry(p[idx], q); qc.rz(p[idx+1], q); idx += 2
        for q in range(n - 1):
            qc.cx(q, q + 1)
    return qc

def _get_hamiltonian() -> SparsePauliOp:
    return SparsePauliOp.from_list([("ZZ", 1.0), ("XI", 0.5), ("IX", 0.5)])

@dataclass
class RunRecord:
    hamiltonian: SparsePauliOp
    depth: int
    method: str
    energies: list = field(default_factory=list)
    final_energy: float = None
    exact_energy: float = None

    @property
    def error(self):
        return abs(self.final_energy - self.exact_energy)

class VQE:
    def __init__(self, hamiltonian=None, depth=2, method="COBYLA"):
        self.H = hamiltonian or _get_hamiltonian()
        self.depth = depth
        self.method = method
        self.iter_count = 0
        self.ansatz = _build_ansatz(self.H.num_qubits, self.depth)
        self.record = RunRecord(self.H, depth, method)

    def cost(self, params, backend=None):
        self.iter_count += 1
        try:
            if backend is not None:
                val = IBMEstimator(backend).run([(self.ansatz, self.H, params)]).result()[0].data.evs
            else:
                raise ValueError()
        except Exception:
            pub = (self.ansatz, self.H, params)
            val = StatevectorEstimator().run([pub]).result()[0].data.evs

        self.record.energies.append(float(val))
        if self.iter_count % 10 == 0:
            print(f"  Iter {self.iter_count:>4}: energy = {val:.6f}")
        return val

    def plot(self):
        import webbrowser, os
        exact = self.record.exact_energy
        plt.figure(figsize=(8, 4))
        plt.plot(self.record.energies, label="VQE energy", color="steelblue")
        plt.axhline(exact, color="red", linestyle="--", label=f"Exact: {exact:.4f}")
        plt.axhline(self.record.final_energy, color="green", linestyle=":",
                    label=f"Final: {self.record.final_energy:.4f}")
        plt.xlabel("Iteration")
        plt.ylabel("Energy")
        plt.title(f"VQE Convergence (depth={self.depth}, method={self.method})")
        plt.legend()
        plt.tight_layout()
        plt.savefig("vqe_run.png", dpi=150)
        webbrowser.open("file://" + os.path.abspath("vqe_run.png"))

    def run(self, backend=None):
        x0 = np.random.uniform(-np.pi, np.pi, self.ansatz.num_parameters)
        result = minimize(partial(self.cost, backend=backend), x0,
                          method=self.method, options={"maxiter": 200})

        self.record.final_energy = result.fun
        self.record.exact_energy = min(np.linalg.eigvalsh(self.H.to_matrix()))

        print(f"\nVQE:   {self.record.final_energy:.6f}")
        print(f"Exact: {self.record.exact_energy:.6f}")
        print(f"Error: {self.record.error:.6f}")

        self.plot()
        return self.record
