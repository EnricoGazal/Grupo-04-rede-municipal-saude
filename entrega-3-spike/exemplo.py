"""Spike ADR-0009 (substitui ADR-0005): roteamento e isolamento em células compartilhadas.

O cenário usa duas cidades pequenas na mesma célula de capacidade. O catálogo
fica indisponível depois do carregamento do mapa, Cidade A sofre uma falha e
recebe um pico, e Cidade B continua processando dentro de sua quota. O teste
também rejeita tenant adulterado no corpo da requisição.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Deque, Dict, List, Tuple


@dataclass(frozen=True)
class Request:
    request_id: str
    token_tenant: str
    body_tenant: str
    sequence: int


@dataclass
class SharedCell:
    cell_id: str
    quotas: Dict[str, int]
    queues: Dict[str, Deque[Request]] = field(default_factory=lambda: defaultdict(deque))
    processed: Dict[str, List[str]] = field(default_factory=lambda: defaultdict(list))
    rejected: List[str] = field(default_factory=list)
    failed_tenants: set[str] = field(default_factory=set)

    def enqueue(self, request: Request) -> bool:
        if request.token_tenant != request.body_tenant:
            self.rejected.append(request.request_id)
            return False
        if request.token_tenant not in self.quotas:
            self.rejected.append(request.request_id)
            return False
        self.queues[request.token_tenant].append(request)
        return True

    def fail_tenant(self, tenant_id: str) -> None:
        self.failed_tenants.add(tenant_id)

    def tick(self) -> None:
        """Processa uma quota por tenant; falha de um tenant não para os outros."""
        for tenant_id, quota in self.quotas.items():
            if tenant_id in self.failed_tenants:
                continue
            for _ in range(quota):
                if not self.queues[tenant_id]:
                    break
                request = self.queues[tenant_id].popleft()
                self.processed[tenant_id].append(request.request_id)

    def pending(self, tenant_id: str) -> int:
        return len(self.queues[tenant_id])


class Catalog:
    def __init__(self, routes: Dict[str, str]) -> None:
        self.routes = dict(routes)
        self.available = True

    def lookup(self, tenant_id: str) -> str:
        if not self.available:
            raise RuntimeError("catalogo indisponivel")
        return self.routes[tenant_id]


class Gateway:
    """Gateway replicado: carrega rota e atende mesmo com catálogo fora."""

    def __init__(self, catalog: Catalog, cells: Dict[str, SharedCell]) -> None:
        self.catalog = catalog
        self.cells = cells
        self.route_map: Dict[str, str] = {}
        self.route_errors: List[str] = []
        self.accepted = 0
        self.rejected = 0

    def refresh_routes(self) -> None:
        for tenant_id in self.catalog.routes:
            self.route_map[tenant_id] = self.catalog.lookup(tenant_id)

    def publish(self, request: Request) -> bool:
        if request.token_tenant != request.body_tenant:
            self.route_errors.append(request.request_id)
            self.rejected += 1
            return False
        cell_id = self.route_map.get(request.token_tenant)
        if cell_id is None:
            self.route_errors.append(request.request_id)
            self.rejected += 1
            return False
        accepted = self.cells[cell_id].enqueue(request)
        self.accepted += int(accepted)
        self.rejected += int(not accepted)
        return accepted


def requests(tenant: str, amount: int, prefix: str) -> List[Request]:
    return [
        Request(f"{prefix}-{n:03d}", tenant, tenant, n)
        for n in range(1, amount + 1)
    ]


def run() -> Dict[str, object]:
    catalog = Catalog({"cidade-a": "pool-1", "cidade-b": "pool-1"})
    pool = SharedCell("pool-1", {"cidade-a": 2, "cidade-b": 2})
    gateway = Gateway(catalog, {"pool-1": pool})

    # O mapa é carregado antes da falha do catálogo.
    gateway.refresh_routes()
    catalog.available = False

    # A recebe quatro vezes mais carga; a quota impede starvation de B.
    for request in requests("cidade-a", 12, "A"):
        gateway.publish(request)
    for request in requests("cidade-b", 3, "B"):
        gateway.publish(request)

    for _ in range(3):
        pool.tick()

    b_before_failure = len(pool.processed["cidade-b"])
    a_before_failure = len(pool.processed["cidade-a"])
    pool.fail_tenant("cidade-a")

    # O catálogo continua fora e B ainda consegue ser roteada pelo mapa em memória.
    for request in requests("cidade-b", 2, "B-late"):
        gateway.publish(request)
    for _ in range(2):
        pool.tick()

    # Tentativa de confundir tenant autenticado e tenant informado no corpo.
    forged = Request("forged-001", "cidade-a", "cidade-b", 999)
    forged_accepted = gateway.publish(forged)

    return {
        "catalogo_fora": catalog.available is False,
        "b_antes_da_falha": b_before_failure,
        "a_antes_da_falha": a_before_failure,
        "a_processados": tuple(pool.processed["cidade-a"]),
        "b_processados": tuple(pool.processed["cidade-b"]),
        "a_pendentes": pool.pending("cidade-a"),
        "b_pendentes": pool.pending("cidade-b"),
        "forged_aceito": forged_accepted,
        "rejeicoes": tuple(gateway.route_errors),
        "isolamento": (
            b_before_failure == 3
            and len(pool.processed["cidade-b"]) == 5
            and len(pool.processed["cidade-a"]) == 6
            and pool.pending("cidade-a") == 6
            and forged_accepted is False
            and "forged-001" in gateway.route_errors
        ),
    }


def print_report(result: Dict[str, object]) -> None:
    print("SPIKE ADR-0005 — roteamento e quota por tenant")
    print(f"catalogo fora apos carga: {result['catalogo_fora']}")
    print(f"cidade-a antes da falha: {result['a_antes_da_falha']}")
    print(f"cidade-b antes da falha: {result['b_antes_da_falha']}")
    print(f"cidade-a processados: {result['a_processados']}")
    print(f"cidade-b processados: {result['b_processados']}")
    print(f"cidade-a pendentes: {result['a_pendentes']}")
    print(f"cidade-b pendentes: {result['b_pendentes']}")
    print(f"tenant adulterado aceito: {result['forged_aceito']}")
    print(f"rejeicoes: {result['rejeicoes']}")
    print(f"isolamento comprovado: {result['isolamento']}")


def main() -> None:
    result = run()
    assert result["isolamento"] is True
    print_report(result)


if __name__ == "__main__":
    main()
