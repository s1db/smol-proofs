# SmolPB: Efficient Trimming of Pseudo-Boolean Proofs

SmolPB is a tool for shortening proofs produced by [VeriPB](https://github.com/StephanGocht/VeriPB).
It traverses the proof tree and removes redundant constraints not required by the solution/contradiction.

## Usage

This repository contains two implementations of trimming algorithms, one using forward checking the other using backward checking. Developed with Python 3.10 and its standard library.

Files:
```
constraint.py: Constraint class.
model.py: Model class for forward checking.
proof.py: Proof class for forward checking.
stack_model.py: Model class for backward checking.
stack_proof.py: Proof class for backward checking.
visualize.py: Visualization of the trimmed proofs on the original proof.
*_pipeline.py: Pipelines for trimming proofs.
tests/: Tests for the trimming algorithms, though poorly implemented.
images2_*/: Images of trimmed proofs produced by the visualizer.
playground/: Scripts for trying out new things/experimenting, not part of the project.
proofs/: A bunch of test cases from various sources.
*_proofs/: The main test cases used for the paper.
priority_set.py: A dodgy data structure without which the backwards checking won't work.
```


Ciaran/Matthew/The future Research Software Engineer, if you ever get around to reading this, I'm sorry for the mess. I'm sure I'll never get around to cleaning it up. Also the backwards checking algorithm doesn't work on the odd test cases of magic_series_proofs and I don't know why, I don't think I ever will. 

I'm sure the future Research Software Engineer will spend a few months to fix it and I'd be more than happy to assist them if they for some odd reason choose not to bin this whole codebase and start fresh, as they should. 😊