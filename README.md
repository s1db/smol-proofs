# SmolPB: Efficient Trimming of Pseudo-Boolean Proofs

SmolPB is a tool for shortening proofs produced by [VeriPB](https://github.com/StephanGocht/VeriPB).
It traverses the proof tree and removes redundant constraints not required by the solution/contradiction.

## Usage

```
python proof.py <model_file>
```
This produces a file `proof_file.rup` which contains the antecedents required by each rup step.

```
python smol_proof.py <model_file>
```
This produces a file `smol_proof_file.pbp` which contains the trimmed proof that can be verified by the proof checker.