"""Genera los tres HTML descriptivos versionados."""
from strategic_overview import generate as generate_strategic
from tactical_diagnosis import generate as generate_tactical
from operational_prioritization import generate as generate_prioritization


if __name__ == "__main__":
    generate_strategic()
    generate_tactical()
    generate_prioritization()
