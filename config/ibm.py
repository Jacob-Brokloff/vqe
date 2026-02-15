from qiskit_ibm_runtime import QiskitRuntimeService

IBM_API_KEY  = "" # add if you want to connect to real QPUs in IBM Cloud
IBM_INSTANCE = "" # add if you want to connect to real QPUs in IBM Cloud
IBM_BACKEND  = ""  # leave blank for least busy

def get_service() -> QiskitRuntimeService | None:
    try:
        if not IBM_API_KEY:
            raise ValueError("No API key provided")
        service = QiskitRuntimeService(
            token=IBM_API_KEY,
            instance=IBM_INSTANCE
        )
        print("Connected to IBM Quantum.")
        return service
    except Exception as e:
        print(f"IBM connection failed ({e}) — falling back to local simulator.")
        return None

def get_backend(service: QiskitRuntimeService = None):
    try:
        service = service or get_service()
        if service is None:
            raise ValueError("No service available")
        backend = service.backend(IBM_BACKEND) if IBM_BACKEND else service.least_busy(operational=True, simulator=False)
        print(f"Using backend: {backend.name}")
        return backend
    except Exception as e:
        print(f"Backend unavailable ({e}) — falling back to local simulator.")
        return None
