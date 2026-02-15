from vqe.vqe import VQE, _get_hamiltonian as get_hamiltonian
from config.ibm import get_backend

if __name__ == "__main__":
    backend = get_backend()
    vqe = VQE(get_hamiltonian(), depth=2)
    record = vqe.run(backend=backend)
