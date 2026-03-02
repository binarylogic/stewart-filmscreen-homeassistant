"""Typed integration models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from stewart_filmscreen.client import StewartFilmscreenClient

if TYPE_CHECKING:
    from .coordinator import StewartFilmscreenCoordinator


@dataclass
class MotorState:
    position: int | None = None
    status: str | None = None


@dataclass
class StewartFilmscreenState:
    authenticated: bool = False
    motors: dict[str, MotorState] = field(default_factory=dict)


@dataclass
class StewartFilmscreenIntegrationData:
    client: StewartFilmscreenClient
    coordinator: StewartFilmscreenCoordinator
