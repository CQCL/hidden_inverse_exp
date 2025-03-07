# Hidden Inverse Circuits for Coherent Error Suppression  
## Hack month week 1
**Key reference:** https://arxiv.org/abs/2104.01119

**Idea:** Self adjoint gates such as CX have two equivalent decompositions into hardware native gates. Find symmetric circuits and use both decompositions to cancel coherent errors.

Contributions and suggestions for future work welcome.

If we have a matrix $M$ satisfying $M=M^\dagger$ we say that $M$ is self adjoint.
We can decompose this matrix $M$ in two ways. 

$$
\begin{equation}
M = ABC = C^\dagger  B^\dagger  A^\dagger = M^\dagger
\end{equation}
$$

Here $M$ represents the unitary (and self-adjoint) matrix associated with a two qubit gate.

![alt text](images/inverses_screenshot.png "Title")

![alt text](images/gadget_screenshot.png "Title")


## Setup

1. Clone this repository

```shell
git@github.com:CQCL/hidden_inverse_exp.git
```

2. Now install dependencies with [uv](https://docs.astral.sh/uv/).

```shell
cd hidden_inverse_exp
uv sync --all-groups
```

3. Run the tests
```shell
cd tests
uv run pytest
```