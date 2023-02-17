# smol-proofs

smol-proofs is a tool for shortening proofs produced by [VeriPB](https://github.com/StephanGocht/VeriPB).
It traverses the proof tree and removes redundant nodes, which are nodes that are not needed to prove the goal.

## Usage

```
python pb_constraint.py <model_file> <proof_file>
```
This produces a file `proof_file.rup` which contains the ancedents required by each rup step.

