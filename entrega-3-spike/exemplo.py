"""Spike ADR-0005: isolamento determinístico entre células de saúde.

O programa simula duas cidades com filas, consumidores e orçamento de
concorrência independentes. Cidade A sofre um pico e depois uma falha; Cidade B
continua processando mensagens. Não usa dependências externas.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import deque
from typing import Deque, Dict, List, Tuple


@dataclass(frozen=True)
class Event:
    event_id: str
    tenant_id: str
    sequence: int
    kind: str = "campaign.request"


@dataclass
class Cell:
    tenant_id: str
    concurrency: int
    queue: Deque[Event] = field(default_factory=deque)
    processed: List[str] = field(default_factory=list)
    rejected: List[str] = field(default_factory=list)
    failed: bool = False

    def enqueue(self, event: Event) -> None:
        if event.tenant_id != self.tenant_id:
            raise ValueError("tenant misturado na fila")
        self.queue.append(event)

    def tick(self) -> None:
        if self.failed:
            return
        for _ in range(self.concurrency):
            if not self.queue:
                break
            event = self.queue.popleft()
            if event.tenant_id != self.tenant_id:
                self.rejected.append(event.event_id)
                continue
            self.processed.append(event.event_id)

    def snapshot(self) -> Tuple[int, int, int, bool]:
        return (len(self.queue), len(self.processed), len(self.rejected), self.failed)


class CellRouter:
    """Catálogo mínimo: resolve tenant para uma célula sem fallback regional."""

    def __init__(self, cells: Dict[str, Cell]) -> None:
        self.cells = cells
        self.routed = 0
        self.route_errors: List[str] = []

    def publish(self, event: Event) -> None:
        cell = self.cells.get(event.tenant_id)
        if cell is None:
            self.route_errors.append(event.event_id)
            return
        cell.enqueue(event)
        self.routed += 1


def make_events(tenant_id: str, amount: int, prefix: str) -> List[Event]:
    return [
        Event(event_id=f"{prefix}-{number:03d}", tenant_id=tenant_id, sequence=number)
        for number in range(1, amount + 1)
    ]


def run_simulation() -> Dict[str, object]:
    city_a = Cell(tenant_id="cidade-a", concurrency=2)
    city_b = Cell(tenant_id="cidade-b", concurrency=2)
    router = CellRouter({"cidade-a": city_a, "cidade-b": city_b})

    # Pico sazonal: A recebe quatro vezes mais eventos que B.
    for event in make_events("cidade-a", 12, "A"):
        router.publish(event)
    for event in make_events("cidade-b", 3, "B"):
        router.publish(event)

    # Três ciclos processam o tráfego normal de B e parte do pico de A.
    for _ in range(3):
        city_a.tick()
        city_b.tick()

    before_failure_b = tuple(city_b.processed)
    city_a.failed = True
    pending_a_at_failure = len(city_a.queue)

    # A falha congela apenas A. B continua recebendo e processando.
    for event in make_events("cidade-b", 2, "B-late"):
        router.publish(event)
    for _ in range(2):
        city_a.tick()
        city_b.tick()

    # Um evento com tenant incorreto nunca entra na célula de A.
    wrong_tenant = Event("B-cross", "cidade-b", 999)
    router.publish(wrong_tenant)

    return {
        "roteados": router.routed,
        "erros_de_rota": tuple(router.route_errors),
        "A_antes_da_falha": before_failure_b[:0],
        "A_estado_final": city_a.snapshot(),
        "B_estado_final": city_b.snapshot(),
        "A_pendente_na_falha": pending_a_at_failure,
        "B_processados": tuple(city_b.processed),
        "isolamento": (
            city_a.failed
            and len(city_b.processed) == 5
            and len(city_a.processed) == 6
            and len(city_a.queue) == 6
            and not city_a.rejected
            and not city_b.rejected
        ),
    }


def print_report(report: Dict[str, object]) -> None:
    print("SPIKE ADR-0005 — isolamento por célula")
    print(f"eventos roteados: {report['roteados']}")
    print(f"erros de rota: {report['erros_de_rota']}")
    print(f"cidade-a estado final: {report['A_estado_final']}")
    print(f"cidade-b estado final: {report['B_estado_final']}")
    print(f"cidade-a pendente na falha: {report['A_pendente_na_falha']}")
    print(f"cidade-b processados: {report['B_processados']}")
    print(f"isolamento comprovado: {report['isolamento']}")


def main() -> None:
    report = run_simulation()
    assert report["erros_de_rota"] == ()
    assert report["isolamento"] is True
    print_report(report)


if __name__ == "__main__":
    main()
