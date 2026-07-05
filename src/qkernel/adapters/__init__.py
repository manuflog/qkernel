"""Input adapters for Q-Kernel.

Adapters are deliberately dependency-light. Heavy SDK adapters, such as Qiskit
or Stim, should translate into these stable table formats first.
"""

from .pauli_table import load_pauli_table, pauli_table_program
from .stim_lite import load_stim_lite_program, parse_stim_lite_text
from .qiskit_lite import load_qiskit_lite_program, parse_qiskit_lite_data

__all__ = ["load_pauli_table", "pauli_table_program", "load_stim_lite_program", "parse_stim_lite_text", "load_qiskit_lite_program", "parse_qiskit_lite_data"]
